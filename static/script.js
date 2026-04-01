document.addEventListener("DOMContentLoaded", () => {
    
    // Core Elements
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const fileInfo = document.getElementById("file-info");
    const fileName = document.getElementById("file-name");
    const analyzeBtn = document.getElementById("analyze-btn");
    
    const uploadSection = document.getElementById("upload-section");
    const loadingSection = document.getElementById("loading-section");
    const resultsSection = document.getElementById("results-section");
    const loadingText = document.getElementById("loading-text");
    const resetBtn = document.getElementById("reset-btn");

    // Results Elements
    const rolesContainer = document.getElementById("roles-container");
    const jobsContainer = document.getElementById("jobs-container");
    const improvementsList = document.getElementById("improvements-list");
    const questionsContainer = document.getElementById("questions-container");

    let selectedFile = null;

    // --- Drag and Drop Logic --- //

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");

        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (file.type !== "application/pdf") {
            alert("Please upload a valid PDF file.");
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileInfo.classList.remove("hidden");
        
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove("disabled");
    }

    // --- Tab Logic --- //
    const tabs = document.querySelectorAll(".tab-btn");
    const panes = document.querySelectorAll(".tab-pane");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            panes.forEach(p => p.classList.add("hidden"));

            tab.classList.add("active");
            document.getElementById(tab.dataset.target).classList.remove("hidden");
        });
    });

    // --- API Request Logic --- //

    const loadingLines = [
        "Extracting PDF Context...",
        "Firing up the Job Finder Agent...",
        "Firing up the Resume Optimizer Agent...",
        "Firing up the Interview Coach Agent...",
        "Analyzing Skills & Technologies...",
        "Finding Real Job Fits...",
        "Almost there..."
    ];

    analyzeBtn.addEventListener("click", async () => {
        if (!selectedFile) return;

        // Switch UI to Loading
        uploadSection.classList.add("hidden");
        loadingSection.classList.remove("hidden");

        // Cycle loading text
        let lineIndex = 0;
        const textInterval = setInterval(() => {
            lineIndex = (lineIndex + 1) % loadingLines.length;
            loadingText.textContent = loadingLines[lineIndex];
        }, 3000);

        try {
            const formData = new FormData();
            formData.append("file", selectedFile);

            const response = await fetch("/api/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            clearInterval(textInterval);

            if (!response.ok) {
                throw new Error(data.error || "Server responded with an error.");
            }

            renderResults(data);

        } catch (error) {
            clearInterval(textInterval);
            alert("Error analyzing resume: " + error.message);
            loadingSection.classList.add("hidden");
            uploadSection.classList.remove("hidden");
        }
    });

    resetBtn.addEventListener("click", () => {
        selectedFile = null;
        fileInfo.classList.add("hidden");
        analyzeBtn.disabled = true;
        fileInput.value = "";
        
        resultsSection.classList.add("hidden");
        uploadSection.classList.remove("hidden");
        
        // Ensure first tab is active again
        tabs[0].click();
    });

    // --- Render Logic --- //

    function renderResults(data) {
        loadingSection.classList.add("hidden");
        resultsSection.classList.remove("hidden");

        // 1. Roles
        rolesContainer.innerHTML = "";
        data.roles.forEach(role => {
            const span = document.createElement("span");
            span.className = "tag";
            span.innerHTML = `<i class="fa-solid fa-star fa-sm"></i> ${role}`;
            rolesContainer.appendChild(span);
        });

        // 2. Jobs
        jobsContainer.innerHTML = "";
        if(data.jobs.length === 0){
             jobsContainer.innerHTML = "<p>No jobs found.</p>";
        } else {
            data.jobs.forEach(job => {
                const card = document.createElement("div");
                card.className = "card";
                
                const matchedHtml = job.matched_skills.map(s => `<span class="matched">${s}</span>`).join("");
                const missingHtml = job.missing_skills.map(s => `<span class="missing">${s}</span>`).join("");

                card.innerHTML = `
                    <div class="card-header">
                        <div>
                            <div class="job-role">${job.role}</div>
                            <div class="job-company"><i class="fa-regular fa-building"></i> ${job.company}</div>
                        </div>
                        <div class="score-badge">${job.match_score}% Match</div>
                    </div>
                    <div class="job-desc">${job.description}</div>
                    
                    <div class="skills-row">
                        <strong>Matched:</strong> ${matchedHtml || "<span>None</span>"}
                    </div>
                    <div class="skills-row">
                        <strong>Missing:</strong> ${missingHtml || "<span>None</span>"}
                    </div>

                    <div class="action-plan">
                        <strong>Priority: ${job.priority}</strong><br>
                        ${job.action_plan}
                    </div>

                    <a href="${job.link}" target="_blank" class="btn-link">Apply on LinkedIn <i class="fa-solid fa-arrow-up-right-from-square fa-sm"></i></a>
                `;
                jobsContainer.appendChild(card);
            });
        }

        // 3. Improvements
        improvementsList.innerHTML = "";
        if(data.improvements.length === 0) {
            improvementsList.innerHTML = "<li>No specific improvements found. Looks solid!</li>";
        } else {
            data.improvements.forEach(imp => {
                const li = document.createElement("li");
                li.textContent = imp;
                improvementsList.appendChild(li);
            });
        }

        // 4. Questions
        questionsContainer.innerHTML = "";
        if(data.questions.length === 0) {
             questionsContainer.innerHTML = "<p>No questions generated.</p>";
        } else {
            data.questions.forEach(q => {
                const card = document.createElement("div");
                card.className = "card question-card";
                
                const badgeClass = q.type.toLowerCase() === "technical" ? "badge-tech" : "badge-behav";
                const icon = q.type.toLowerCase() === "technical" ? "fa-code" : "fa-users";

                card.innerHTML = `
                    <div style="font-size:0.8rem; font-weight:600; text-transform:uppercase; margin-bottom:0.5rem; letter-spacing:1px;" class="${badgeClass}">
                        <i class="fa-solid ${icon}"></i> ${q.type}
                    </div>
                    <h4>${q.question}</h4>
                    <div class="tip"><strong>Coach's Tip:</strong> ${q.tip}</div>
                `;
                questionsContainer.appendChild(card);
            });
        }
    }
});
