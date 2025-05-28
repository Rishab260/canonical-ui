document.addEventListener("DOMContentLoaded", () => {
  // --- Screenshots Slider ---
  const slidesContainer = document.querySelector(
    "#screenshots-section .slides"
  );
  const slides = Array.from(
    document.querySelectorAll("#screenshots-section .slide")
  );
  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  const dotsContainer = document.querySelector(
    "#screenshots-section .slider-dots"
  );

  if (slidesContainer && slides.length > 0) {
    let currentIndex = 0;
    const visibleSlides = 3; // Number of slides to show at a time
    const slideWidth = slides[0].offsetWidth + 20; // slide width + gap

    // Create dots
    slides.forEach((_, index) => {
      const dot = document.createElement("span");
      dot.classList.add("dot");
      if (index === currentIndex) dot.classList.add("active");
      dot.addEventListener("click", () => {
        goToSlide(index);
      });
      dotsContainer.appendChild(dot);
    });
    const dots = Array.from(dotsContainer.children);

    function updateSlider() {
      let offset = 0;
      if (slides.length > visibleSlides) {
        const targetCenterIndexInView = Math.floor(visibleSlides / 2);
        let centeringOffset = targetCenterIndexInView * slideWidth;
        offset = -(currentIndex * slideWidth - centeringOffset);

        const maxOffset = 0;
        const minOffset = -((slides.length - visibleSlides) * slideWidth);
        offset = Math.max(minOffset, Math.min(maxOffset, offset));
      } else {
        offset = 0;
      }

      slidesContainer.style.transform = `translateX(${offset}px)`;

      slides.forEach((slide, index) => {
        slide.classList.toggle("active", index === currentIndex);
      });

      dots.forEach((dot, index) => {
        dot.classList.toggle("active", index === currentIndex);
      });

      prevBtn.classList.toggle("hidden", currentIndex === 0);
      nextBtn.classList.toggle(
        "hidden",
        currentIndex >= slides.length - 1 || slides.length <= visibleSlides
      );

      if (slides.length <= visibleSlides) {
        prevBtn.classList.add("hidden");
        nextBtn.classList.add("hidden");
      }
    }

    function goToSlide(index) {
      currentIndex = Math.max(0, Math.min(index, slides.length - 1));
      updateSlider();
    }

    nextBtn.addEventListener("click", () => {
      if (currentIndex < slides.length - 1) {
        goToSlide(currentIndex + 1);
      }
    });

    prevBtn.addEventListener("click", () => {
      if (currentIndex > 0) {
        goToSlide(currentIndex - 1);
      }
    });

    slides[currentIndex].classList.add("active");
    updateSlider();

    window.addEventListener("resize", updateSlider);
  } else {
    if (prevBtn) prevBtn.style.display = "none";
    if (nextBtn) nextBtn.style.display = "none";
    if (dotsContainer) dotsContainer.style.display = "none";
  }

  // --- About Section Read More ---
  const aboutText = document.getElementById("about-text");
  const readMoreBtn = document.getElementById("read-more-btn");

  if (readMoreBtn) {
    readMoreBtn.addEventListener("click", () => {
      if (aboutText.classList.contains("expanded")) {
        aboutText.classList.remove("expanded");
        readMoreBtn.textContent = "Read More";
      } else {
        aboutText.classList.add("expanded");
        readMoreBtn.textContent = "Read Less";
      }
    });
  }

  // --- Smooth Scrolling & Active Nav Link ---
  const navLinks = document.querySelectorAll("#main-header nav ul li a");
  const sections = document.querySelectorAll("main section");

  function changeNavActiveState() {
    let currentSectionId = "";
    sections.forEach((section) => {
      const sectionTop = section.offsetTop - 100;
      if (pageYOffset >= sectionTop) {
        currentSectionId = section.getAttribute("id");
      }
    });

    navLinks.forEach((link) => {
      link.classList.toggle(
        "active",
        link.getAttribute("href") === `#${currentSectionId}`
      );
    });
  }

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 70,
          behavior: "smooth",
        });
      }
    });
  });

  window.addEventListener("scroll", changeNavActiveState);
  changeNavActiveState();

  // --- Form Handling ---
  const feedbackForm = document.getElementById("feedback-form");
  if (feedbackForm) {
    feedbackForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const name = document.getElementById("name").value;
      const email = document.getElementById("email").value;
      const question = document.getElementById("question").value;

      if (!name.trim() || !email.trim() || !question.trim()) {
        alert("Please fill in all required fields (Name, Email, Question).");
        return;
      }

      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(email)) {
        alert("Please enter a valid email address.");
        return;
      }

      alert("Form submitted! Thank you for your feedback.");
      this.reset();
      const fileNameDisplay = document.querySelector(".file-name-display");
      if (fileNameDisplay) fileNameDisplay.textContent = "No file chosen";
    });
  }

  const fileInput = document.getElementById("file-upload");
  const fileNameDisplay = document.querySelector(
    ".file-upload-group .file-name-display"
  );

  if (fileInput && fileNameDisplay) {
    fileInput.addEventListener("change", function () {
      fileNameDisplay.textContent =
        this.files.length > 0 ? this.files[0].name : "No file chosen";
    });
  }
});