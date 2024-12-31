document.addEventListener("DOMContentLoaded", function() {
  console.log("UI Tables JS Loaded!");

  const tableHeaders = document.querySelectorAll("th");

  // Sort table by clicking headers
  tableHeaders.forEach(header => {
      header.addEventListener("click", function() {
          const index = Array.from(tableHeaders).indexOf(header);
          sortTable(index);
      });
  });

  // Sorting function
  function sortTable(index) {
      const table = document.querySelector("table");
      const rows = Array.from(table.rows).slice(1); // Skip the header row
      const isAscending = table.classList.contains("ascending");

      rows.sort((rowA, rowB) => {
          const cellA = rowA.cells[index].innerText;
          const cellB = rowB.cells[index].innerText;
          return (cellA > cellB ? 1 : -1) * (isAscending ? 1 : -1);
      });

      rows.forEach(row => table.appendChild(row)); // Re-order rows
      table.classList.toggle("ascending", !isAscending);
  }

  // Add event listener for form submission (Add users)
  const targetForm = document.getElementById("targetForm");
  targetForm.addEventListener("submit", handleFormSubmit);

  // Check if email exists
  function checkIfEmailExists(email) {
      return fetch(`/check-email-exists/?email=${email}`)
          .then(response => response.json())
          .then(data => data.exists) // Return true if email exists, false otherwise
          .catch(err => {
              console.error("Error checking email:", err);
              return false;
          });
  }

  // Handle form submission
  function handleFormSubmit(event) {
      event.preventDefault();

      const email = document.getElementById("email").value.trim();
      const firstName = document.getElementById("firstName").value.trim();
      const lastName = document.getElementById("lastName").value.trim();
      const position = document.getElementById("position").value.trim();

      // Check if all required fields are filled
      if (!firstName || !lastName || !email) {
          alert("First Name, Last Name, and Email are required!");
          return;
      }

      // Check if email already exists in the database
      checkIfEmailExists(email).then(exists => {
          if (exists) {
              alert("Email is already in use. Please enter a different email.");
          } else {
              // If email is unique, proceed with adding the user
              const newRow = document.createElement("tr");
              newRow.innerHTML = `
                  <td>${firstName}</td>
                  <td>${lastName}</td>
                  <td>${email}</td>
                  <td>${position}</td>
                  <td>
                      <button class="btn btn-danger btn-sm" onclick="deleteUserRow(this)">Delete</button>
                  </td>
              `;
              document.querySelector("#targetsTable tbody").appendChild(newRow);
              targetForm.reset();
          }
      });
  }

  // Function to delete a user row
  function deleteUserRow(button) {
      const row = button.closest("tr");
      row.remove();
  }

  // Save group and users to the database
  function saveGroupData() {
      const groupName = document.getElementById("name").value.trim();
      const users = [];

      // Collect users from the modal table
      document.querySelectorAll("#targetsTable tbody tr").forEach(row => {
          const cells = row.querySelectorAll("td");
          users.push({
              firstName: cells[0].textContent,
              lastName: cells[1].textContent,
              email: cells[2].textContent,
              position: cells[3].textContent
          });
      });

      if (!groupName || users.length === 0) {
          alert("Group name and at least one user are required!");
          return;
      }

      // Get CSRF token (Method 1)
      const csrfToken = document.getElementById("csrf_token").value;

      // Send data to backend for saving
      fetch("/save-group/", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken // Add CSRF token here
          },
          body: JSON.stringify({ group_name: groupName, users: users })
      })
      .then(response => response.json())
      .then(data => {
          if (data.error) {
              alert(`Error: ${data.error}`);
          } else {
              alert("Group saved successfully!");
              $('#modal').modal('hide'); // Close modal
              loadGroups(); // Refresh groups
          }
      })
      .catch(err => console.error("Error saving group:", err));
  }

  // Load groups when the page is loaded
  function loadGroups() {
      fetch("/groups/")
          .then(response => response.json())
          .then(data => {
              const groupTable = document.getElementById("groupTable");
              const mainTableBody = document.querySelector("#groupTable tbody");
              const noProfileMessage = document.getElementById("noProfileMessage");

              mainTableBody.innerHTML = ""; // Clear existing rows

              if (data.groups.length === 0) {
                  noProfileMessage.style.display = "block"; // Show no profile message
                  groupTable.style.display = "none"; // Hide table
              } else {
                  noProfileMessage.style.display = "none"; // Hide no profile message
                  groupTable.style.display = "table"; // Show table

                  data.groups.forEach(group => {
                      const newRow = document.createElement("tr");
                      newRow.innerHTML = `
                          <td>${group.name}</td>
                          <td>${group.user_count}</td>
                          <td>${group.updated_at}</td>
                          <td>
                              <button class="btn btn-danger btn-sm" onclick="deleteGroup(${group.id})">Delete</button>
                              <button class="btn btn-info btn-sm" onclick="editGroup(${group.id})">Edit</button>
                          </td>
                      `;
                      mainTableBody.appendChild(newRow);
                  });
              }
          })
          .catch(err => console.error("Error loading groups:", err));
  }

  // Edit group function
  function editGroup(groupId) {
      // Redirect to an edit page or open a modal to edit the group
      window.location.href = `/edit-group/${groupId}/`;  // Example URL
  }

  // Delete group
  function deleteGroup(groupId) {
    if (confirm("Are you sure you want to delete this group?")) {
        fetch(`/delete-group/${groupId}/`, { method: "DELETE" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Group deleted successfully!");
                    loadGroups(); // Refresh groups
                } else {
                    alert("Error deleting group!");
                }
            });
    }
}

function editGroup(groupId) {
    // Fetch group data for editing (optional: you can preload data into modal for editing)
    fetch(`/group-details/${groupId}/`)
        .then(response => response.json())
        .then(data => {
            groupNameInput.value = data.group.name;
            loadUsersForGroup(groupId);
            $('#modal').modal('show');
        })
        .catch(err => console.error("Error loading group details:", err));
}

  // Call loadGroups when the page is loaded
  loadGroups();
});


function loadGroups() {
  fetch("/groups/")  // Make sure the URL matches your backend route
      .then(response => response.json())
      .then(data => {
          groupTableBody.innerHTML = ""; // Clear existing rows
          data.groups.forEach(group => {
              const newRow = document.createElement("tr");
              newRow.innerHTML = `
                  <td>${group.name}</td>
                  <td>${group.user_count}</td>
                  <td>${group.updated_at}</td>
                  <td>
                      <button class="btn btn-danger btn-sm" onclick="deleteGroup(${group.id})">Delete</button>
                      <button class="btn btn-info btn-sm" onclick="editGroup(${group.id})">Edit</button>
                  </td>
              `;
              groupTableBody.appendChild(newRow);
          });
      })
      .catch(err => console.error("Error loading groups:", err));
}

function deleteGroup(groupId) {
  if (confirm("Are you sure you want to delete this group?")) {
      fetch(`/delete-group/${groupId}/`, { method: 'DELETE' })
          .then(response => response.json())
          .then(data => {
              if (data.message) {
                  alert(data.message); // Show success message
                  loadGroups(); // Refresh groups after deletion
              }
          })
          .catch(err => console.error("Error deleting group:", err));
  }
}

function editGroup(groupId) {
    fetch(`/group-details/${groupId}/`)
        .then(response => {
            // Check if the response is ok and contains JSON
            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }
            return response.json();  // Parse response as JSON
        })
        .then(data => {
            // Proceed with using the data
            if (data.group) {
                const groupNameInput = document.getElementById("name");
                groupNameInput.value = data.group.name;
                loadUsersForGroup(groupId);  // Load users when editing group
                $('#modal').modal('show');
            } else {
                console.error("Error: Group details not found.");
            }
        })
        .catch(err => {
            console.error("Error loading group details:", err);
        });
}


document.addEventListener("DOMContentLoaded", function () {
    const csvUploadInput = document.getElementById("csvupload");
  
    // Add an event listener to handle file selection
    csvUploadInput.addEventListener('change', function (event) {
      const file = event.target.files[0]; // Get the first file
  
      if (!file) {
        return;
      }
  
      // Check the file type is CSV
      if (file.type !== "text/csv") {
        alert("Please select a CSV file.");
        return;
      }
  
      const formData = new FormData();
      formData.append("csvupload", file); // Append the selected file to the FormData
  
      // Optionally add the group ID
      const groupId = document.getElementById('group_id_input').value; // Assuming there's an input field for group ID
      formData.append("group_id", groupId);
  
      // Send the file to the backend for processing
      fetch("/bulk-import/", {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": "{{ csrf_token }}" // Include CSRF token if needed
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.message) {
          alert(data.message);
          loadGroups(); // Refresh groups after successful import
        } else {
          alert("Error importing users: " + data.error);
        }
      })
      .catch(err => {
        console.error("Error uploading CSV:", err);
        alert("An error occurred while uploading the file.");
      });
    });
  });
  