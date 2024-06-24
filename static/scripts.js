let lastKeywords = ""; // Initialize lastKeywords at the top

document
  .getElementById("searchForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    let keywords = document.getElementById("keywords").value;
    keywords = keywords.split(",").map((keyword) => keyword.trim());

    // Check if the current keywords are the same as the last ones
    if (keywords.join(",") === lastKeywords) {
      Toastify({
        text: "Keywords have not changed",
        duration: 3000,
        gravity: "top",
        position: "right",
        stopOnFocus: true,
        style: {
          background: "rgb(255, 0, 0)",
          color: "#fff",
        },
      }).showToast();
      return;
    }

    // Store the current keywords as the last keywords
    lastKeywords = keywords.join(",");

    // Disable the submit button
    const searchButton = document.getElementById("search-button");
    searchButton.disabled = true;

    try {
      let results = document.getElementById("results");
      results.innerHTML = ""; // Clear previous results

      // Show spinner
      document.getElementById("spinner").style.display = "inline-block";

      let response = await fetch("/search_groups", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ keywords: keywords }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      let data = await response.json();
      if (data.status === "success") {
        data.data.forEach((group) => {
          // Create a new <li> element with class "list-item"
          let listItem = document.createElement("li");
          listItem.classList.add("list-item");
          listItem.innerHTML = `
            <div class="group-wrapper"> 
              <p>${group.title}</p>
              <div>
                <p class="members-wrapper">
                  <span><strong>${Intl.NumberFormat().format(
                    group.members
                  )}</strong></span>
                  <img src="/static/members-icon.svg">
                </p>
              </div>
            </div>
          `;

          // Add click event listener to copy text content
          listItem.addEventListener("click", () => {
            if (group.url) {
              window.open(group.url, "_blank");
            } else {
              Toastify({
                text: `Link not available for: ${group.title}`,
                duration: 3000,
                gravity: "top",
                position: "right",
                stopOnFocus: true,
                style: {
                  background: "rgb(255, 0, 0)",
                  color: "#fff",
                },
              }).showToast();
            }
          });

          // Append the <li> to the results list
          results.appendChild(listItem);
        });
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while searching for groups.");
    } finally {
      // Hide spinner
      document.getElementById("spinner").style.display = "none";
      //Enable the submit button
      searchButton.disabled = false;
    }
  });
