"""Main entry point for Linear Calendar application."""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import requests
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use template/static paths from within the package
package_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(package_dir, 'templates')
static_dir = os.path.join(package_dir, 'static')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)
CORS(app)  # Enable CORS for all routes

# Configuration
LINEAR_API_KEY = os.getenv('LINEAR_API_KEY')
LINEAR_API_URL = "https://api.linear.app/graphql"

if not LINEAR_API_KEY:
    raise ValueError("LINEAR_API_KEY environment variable is not set. Please set it in your .env file.")

def get_linear_headers():
    return {
        "Authorization": f"{LINEAR_API_KEY}",  # Linear API doesn't use Bearer prefix
        "Content-Type": "application/json"
    }

@app.route('/')
def index():
    """Render the main calendar page"""
    return render_template('index.html')

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Fetch teams from Linear API"""
    app.logger.info("API request: Fetching teams from Linear")
    try:
        # GraphQL query to fetch teams
        query = """
        query {
          teams {
            nodes {
              id
              name
              key
              color
            }
          }
        }
        """
        
        app.logger.debug("Sending GraphQL query to Linear API for teams")
        response = requests.post(
            LINEAR_API_URL,
            headers=get_linear_headers(),
            json={"query": query}
        )
        
        app.logger.debug(f"Linear API response status: {response.status_code}")
        
        # Check for API errors
        if response.status_code != 200:
            app.logger.error(f"Linear API error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Linear API returned status code {response.status_code}: {response.text}"}), 500
            
        data = response.json()
        
        if "errors" in data:
            app.logger.error(f"Linear API GraphQL errors: {data['errors']}")
            return jsonify({"error": f"Linear API returned errors: {data['errors']}"}), 500
            
        teams = data.get("data", {}).get("teams", {}).get("nodes", [])
        app.logger.info(f"Successfully fetched {len(teams)} teams from Linear API")
        return jsonify(teams)
    except Exception as e:
        app.logger.exception("Exception while fetching teams from Linear API")
        return jsonify({"error": f"Failed to fetch data from Linear API: {str(e)}"}), 500


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Fetch projects from Linear API"""
    app.logger.info("API request: Fetching projects from Linear")
    try:
        # GraphQL query to fetch projects
        query = """
        query {
          projects {
            nodes {
              id
              name
              color
            }
          }
        }
        """
        
        app.logger.debug("Sending GraphQL query to Linear API for projects")
        response = requests.post(
            LINEAR_API_URL,
            headers=get_linear_headers(),
            json={"query": query}
        )
        
        app.logger.debug(f"Linear API response status: {response.status_code}")
        
        # Check for API errors
        if response.status_code != 200:
            app.logger.error(f"Linear API error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Linear API returned status code {response.status_code}: {response.text}"}), 500
            
        data = response.json()
        
        if "errors" in data:
            app.logger.error(f"Linear API GraphQL errors: {data['errors']}")
            return jsonify({"error": f"Linear API returned errors: {data['errors']}"}), 500
            
        projects = data.get("data", {}).get("projects", {}).get("nodes", [])
        app.logger.info(f"Successfully fetched {len(projects)} projects from Linear API")
        return jsonify(projects)
    except Exception as e:
        app.logger.exception("Exception while fetching projects from Linear API")
        return jsonify({"error": f"Failed to fetch data from Linear API: {str(e)}"}), 500

@app.route('/api/issues', methods=['GET'])
def get_issues():
    """Fetch issues from Linear API with optional filters"""
    app.logger.info("API request: Fetching issues from Linear")
    
    # Get filter parameters
    team_id = request.args.get('teamId')
    project_ids = request.args.getlist('projectId')
    state_id = request.args.get('stateId')
    no_due_date = request.args.get('noDueDate')
    
    try:
        # Build filter conditions
        filters = []
        
        if team_id and team_id != 'all':
            filters.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')

        if project_ids:
            # Create a string representation of the list of IDs for the GraphQL query
            project_filter = json.dumps(project_ids)
            filters.append(f'project: {{ id: {{ in: {project_filter} }} }}')
            
        if state_id and state_id != 'all':
            filters.append(f'state: {{ id: {{ eq: "{state_id}" }} }}')
            
        if no_due_date == 'true':
            filters.append('dueDate: { null: true }')
        else:
            filters.append('dueDate: { null: false }')
        
        # Convert filters to GraphQL format
        filter_string = ", ".join(filters)
        
        # GraphQL query with filters
        query = f"""
        query {{
          issues(filter: {{ {filter_string} }}) {{
            nodes {{
              id
              title
              description
              dueDate
              state {{
                id
                name
                color
              }}
              team {{
                id
                name
                key
              }}
              project {{
                id
                name
              }}
              assignee {{
                id
                name
              }}
              labels {{
                nodes {{
                  id
                  name
                  color
                }}
              }}
            }}
          }}
        }}
        """
        
        app.logger.debug("Sending GraphQL query to Linear API for issues")
        response = requests.post(
            LINEAR_API_URL,
            headers=get_linear_headers(),
            json={"query": query}
        )
        
        app.logger.debug(f"Linear API response status: {response.status_code}")
        
        # Check for API errors
        if response.status_code != 200:
            app.logger.error(f"Linear API error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Linear API returned status code {response.status_code}: {response.text}"}), 500
            
        data = response.json()
        
        if "errors" in data:
            app.logger.error(f"Linear API GraphQL errors: {data['errors']}")
            return jsonify({"error": f"Linear API returned errors: {data['errors']}"}), 500
            
        issues = data.get("data", {}).get("issues", {}).get("nodes", [])
        
        # Process issues to include label nodes directly
        for issue in issues:
            if issue.get("labels") and issue["labels"].get("nodes"):
                issue["labels"] = issue["labels"]["nodes"]
            else:
                issue["labels"] = []
                
        app.logger.info(f"Successfully fetched {len(issues)} issues from Linear API")
        return jsonify(issues)
        
    except Exception as e:
        app.logger.exception("Exception while fetching issues from Linear API")
        return jsonify({"error": f"Failed to fetch data from Linear API: {str(e)}"}), 500


@app.route('/api/states', methods=['GET'])
def get_states():
    """Fetch workflow states from Linear API"""
    app.logger.info("API request: Fetching workflow states from Linear")
    team_id = request.args.get('teamId')
    
    if not team_id:
        return jsonify({"error": "teamId query parameter is required"}), 400
        
    try:
        query = f"""
        query {{
          workflowStates(filter: {{ team: {{ id: {{ eq: "{team_id}" }} }} }}) {{
            nodes {{
              id
              name
              color
              type
            }}
          }}
        }}
        """
        
        app.logger.debug("Sending GraphQL query to Linear API for workflow states")
        response = requests.post(
            LINEAR_API_URL,
            headers=get_linear_headers(),
            json={"query": query}
        )
        
        app.logger.debug(f"Linear API response status: {response.status_code}")
        
        # Check for API errors
        if response.status_code != 200:
            app.logger.error(f"Linear API error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Linear API returned status code {response.status_code}: {response.text}"}), 500
            
        data = response.json()
        
        if "errors" in data:
            app.logger.error(f"Linear API GraphQL errors: {data['errors']}")
            return jsonify({"error": f"Linear API returned errors: {data['errors']}"}), 500
            
        states = data.get("data", {}).get("workflowStates", {}).get("nodes", [])
        app.logger.info(f"Successfully fetched {len(states)} workflow states from Linear API")
        return jsonify(states)
    except Exception as e:
        app.logger.exception("Exception while fetching workflow states from Linear API")
        return jsonify({"error": f"Failed to fetch data from Linear API: {str(e)}"}), 500

def main():
    """Entry point for the application when run as a module."""
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("Starting Linear Calendar application")
    app.logger.info(f"API key configured: {LINEAR_API_KEY[:4]}...{LINEAR_API_KEY[-4:] if LINEAR_API_KEY else 'None'}")
    
    # For Flask, it's better to use the built-in development server for simplicity
    # or use Gunicorn for production
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5001)))

if __name__ == '__main__':
    main()
