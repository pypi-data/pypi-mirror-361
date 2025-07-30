// Simple test script to initialize calendar
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded');
  
  // Check if calendar element exists
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) {
    console.error('Calendar element not found');
    return;
  }
  
  console.log('Calendar element found');
  
  // Check if FullCalendar is available
  if (typeof FullCalendar === 'undefined') {
    console.error('FullCalendar library not loaded');
    return;
  }
  
  console.log('FullCalendar library loaded');
  
  try {
    // Initialize a basic calendar
    const calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth'
    });
    
    calendar.render();
    console.log('Calendar rendered successfully');
  } catch (error) {
    console.error('Error initializing calendar:', error);
  }
});
