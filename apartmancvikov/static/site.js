"use strict";

const navMenu = document.querySelector(".nav-menu");

if (navMenu) {
  const desktopNavigation = window.matchMedia("(min-width: 54rem)");
  const syncNavigation = () => {
    navMenu.open = desktopNavigation.matches;
  };

  syncNavigation();
  desktopNavigation.addEventListener("change", syncNavigation);
}

const lightbox = document.querySelector("#lightbox");

if (lightbox && typeof lightbox.showModal === "function") {
  const lightboxImage = lightbox.querySelector("img");
  const lightboxCaption = lightbox.querySelector("figcaption");
  const previousButton = lightbox.querySelector(".lightbox__nav--previous");
  const nextButton = lightbox.querySelector(".lightbox__nav--next");
  const lightboxLinks = Array.from(
    document.querySelectorAll("[data-lightbox]"),
  );
  let currentImage = 0;
  let touchStart = null;
  let suppressClickUntil = 0;

  const showImage = (index) => {
    currentImage = (index + lightboxLinks.length) % lightboxLinks.length;
    const link = lightboxLinks[currentImage];

    lightboxImage.src = link.href;
    lightboxImage.alt = link.querySelector("img")?.alt || "";
    lightboxCaption.textContent = link.dataset.caption || "";

    if (lightboxLinks.length > 1) {
      const nextImage = new Image();
      nextImage.src =
        lightboxLinks[(currentImage + 1) % lightboxLinks.length].href;
    }
  };

  const navigate = (step) => {
    if (lightboxLinks.length > 1) {
      showImage(currentImage + step);
    }
  };

  previousButton.hidden = lightboxLinks.length < 2;
  nextButton.hidden = lightboxLinks.length < 2;
  lightbox.classList.toggle("lightbox--gallery", lightboxLinks.length > 1);

  lightboxLinks.forEach((link, index) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      showImage(index);
      lightbox.showModal();
      document.documentElement.classList.add("lightbox-open");
    });
  });

  previousButton.addEventListener("click", () => navigate(-1));
  nextButton.addEventListener("click", () => navigate(1));

  lightboxImage.addEventListener("click", (event) => {
    if (performance.now() < suppressClickUntil) {
      return;
    }

    const imageBounds = lightboxImage.getBoundingClientRect();
    const step =
      event.clientX < imageBounds.left + imageBounds.width / 2 ? -1 : 1;
    navigate(step);
  });

  lightboxImage.addEventListener("touchstart", (event) => {
    if (event.touches.length === 1 && lightboxLinks.length > 1) {
      const touch = event.touches[0];
      touchStart = { x: touch.clientX, y: touch.clientY };
    }
  });

  lightboxImage.addEventListener(
    "touchmove",
    (event) => {
      if (!touchStart || event.touches.length !== 1) {
        return;
      }

      const touch = event.touches[0];
      const movementX = touch.clientX - touchStart.x;
      const movementY = touch.clientY - touchStart.y;

      if (Math.abs(movementX) > Math.abs(movementY)) {
        event.preventDefault();
      }
    },
    { passive: false },
  );

  lightboxImage.addEventListener("touchend", (event) => {
    if (!touchStart || event.changedTouches.length === 0) {
      return;
    }

    const touch = event.changedTouches[0];
    const movementX = touch.clientX - touchStart.x;
    const movementY = touch.clientY - touchStart.y;
    touchStart = null;

    if (
      Math.abs(movementX) >= 45 &&
      Math.abs(movementX) > Math.abs(movementY)
    ) {
      suppressClickUntil = performance.now() + 500;
      navigate(movementX > 0 ? -1 : 1);
    }
  });

  lightboxImage.addEventListener("touchcancel", () => {
    touchStart = null;
  });

  lightbox.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      navigate(-1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      navigate(1);
    }
  });

  lightbox.querySelector(".lightbox__close").addEventListener("click", () => {
    lightbox.close();
  });

  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) {
      lightbox.close();
    }
  });

  lightbox.addEventListener("close", () => {
    document.documentElement.classList.remove("lightbox-open");
  });
}
