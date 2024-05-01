const gohsForm = document.getElementById('gohs-form');

gohsForm.addEventListener('submit', (event) => {
  event.preventDefault(); // Prevent default form submission

  // Get values from the form fields
  const date = document.getElementById('date').value;
  // ... get other field values ...

  // Perform validation if needed

  // Submit the data to the server or perform other actions
  // You can use AJAX to send the data without reloading the page
  // ... 
});