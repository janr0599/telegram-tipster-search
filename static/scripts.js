let lastKeywords = "";
let lastDate = "";
let lastMembers = "";
let lastViews = "";
let lastLanguage = "";

document
  .getElementById("searchForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    let keywords = document.getElementById("keywords").value;
    let date = document.getElementById("date").value;
    let members = document.getElementById("members").value;
    let views = document.getElementById("views").value;
    let language = document.getElementById("language").value;

    keywords = keywords.split(",").map((keyword) => keyword.trim());

    // Check if none of the fields have changed
    if (
      keywords.join(",") === lastKeywords &&
      date === lastDate &&
      members === lastMembers &&
      views === lastViews &&
      language === lastLanguage
    ) {
      Toastify({
        text: "No fields have changed",
        duration: 3000,
        gravity: "top",
        position: "right",
        stopOnFocus: true,
        style: {
          background: "rgb(255, 0, 0)",
          color: "#fff",
          borderRadius: "10px",
        },
      }).showToast();
      return;
    }

    // Store the current values as the last values
    lastKeywords = keywords.join(",");
    lastDate = date;
    lastMembers = members;
    lastViews = views;
    lastLanguage = language;

    // Disable the submit button
    const searchButton = document.getElementById("search-button");
    searchButton.disabled = true;

    try {
      let results = document.getElementById("results");
      results.innerHTML = ""; // Clear previous results

      // Show spinner
      document.getElementById("spinner").style.display = "inline-block";

      // data payload
      let requestData = {
        keywords: keywords,
        date: date,
        members: members,
        views: views,
        language: language,
      };

      let response = await fetch("/search_groups", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      let data = await response.json();
      if (data.status === "success") {
        if (data.data.length === 0) {
          // No results found
          let noResults = document.createElement("p");
          noResults.textContent = "No results found";
          results.appendChild(noResults);
        } else {
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

            // Add click event listener to open link
            listItem.addEventListener("click", () => {
              if (group.url) {
                window.open(group.url, "_blank");
              } else {
                Toastify({
                  text: "Link not available",
                  duration: 3000,
                  gravity: "top",
                  position: "right",
                  stopOnFocus: true,
                  style: {
                    background: "rgb(255, 0, 0)",
                    color: "#fff",
                    borderRadius: "10px",
                  },
                }).showToast();
              }
            });

            // Append the <li> to the results list
            results.appendChild(listItem);
          });
        }
      } else if (data.error === "rate_limit") {
        let waitTimeHours = Math.round(data.wait_time / 3600);
        let timeDescription = waitTimeHours > 1 ? "hours" : "hour";
        Toastify({
          text: `Rate limit hit. Please wait for ${waitTimeHours} ${timeDescription} and try again.`,
          duration: 3000,
          gravity: "top",
          position: "right",
          stopOnFocus: true,
          style: {
            background: "rgb(255, 165, 0)",
            color: "#fff",
            borderRadius: "10px",
          },
        }).showToast();
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      console.error("Error:", error);
      Toastify({
        text: "An error occurred while searching for groups.",
        duration: 3000,
        gravity: "top",
        position: "right",
        stopOnFocus: true,
        style: {
          background: "rgb(255, 165, 0)",
          color: "#fff",
          borderRadius: "10px",
        },
      }).showToast();
    } finally {
      // Hide spinner
      document.getElementById("spinner").style.display = "none";
      // Enable the submit button
      searchButton.disabled = false;
    }
  });
