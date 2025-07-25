document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("searchInput");
  const clearBtn = document.getElementById("clearBtn");
  const jobs = document.querySelectorAll(".job-listing");

  function filterJobs() {
    const query = input.value.toLowerCase();
    jobs.forEach(job => {
      const title = job.dataset.title.toLowerCase();
      const company = job.dataset.company.toLowerCase();
      const match = title.includes(query) || company.includes(query);
      job.style.display = match ? "block" : "none";
    });
  }

  input.addEventListener("input", filterJobs);

  clearBtn.addEventListener("click", () => {
    input.value = "";
    filterJobs();
  });
});
