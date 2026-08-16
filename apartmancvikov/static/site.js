"use strict";

const navMenu = document.querySelector(".nav-menu");

if (navMenu) {
  const desktopNavigation = window.matchMedia("(min-width: 68rem)");
  const syncNavigation = () => {
    navMenu.open = desktopNavigation.matches;
  };

  syncNavigation();
  desktopNavigation.addEventListener("change", syncNavigation);
}

const lightbox = document.querySelector("#lightbox");

if (lightbox && typeof lightbox.showModal === "function") {
  const lightboxImage = lightbox.querySelector("img");
  const imageStage = lightbox.querySelector(".lightbox__image-stage");
  const lightboxCaption = lightbox.querySelector("figcaption");
  const zoomButton = lightbox.querySelector(".lightbox__zoom");
  const previousButton = lightbox.querySelector(".lightbox__nav--previous");
  const nextButton = lightbox.querySelector(".lightbox__nav--next");
  const lightboxLinks = Array.from(
    document.querySelectorAll("[data-lightbox]"),
  );
  const maxZoom = 4;
  const toggleZoom = 2.5;
  let currentImage = 0;
  let zoomScale = 1;
  let zoomX = 0;
  let zoomY = 0;
  let gestureStart = null;
  let pinchStart = null;
  let lastTap = null;
  let mouseDrag = null;
  let suppressClickUntil = 0;

  const clamp = (value, minimum, maximum) =>
    Math.min(maximum, Math.max(minimum, value));

  const setZoom = (scale, x, y) => {
    zoomScale = clamp(scale, 1, maxZoom);

    const maxX = Math.max(
      0,
      (lightboxImage.offsetWidth * zoomScale - imageStage.clientWidth) / 2,
    );
    const maxY = Math.max(
      0,
      (lightboxImage.offsetHeight * zoomScale - imageStage.clientHeight) / 2,
    );

    zoomX = clamp(x, -maxX, maxX);
    zoomY = clamp(y, -maxY, maxY);
    lightboxImage.style.transform = `translate3d(${zoomX}px, ${zoomY}px, 0) scale(${zoomScale})`;

    const isZoomed = zoomScale > 1.01;
    lightbox.classList.toggle("lightbox--zoomed", isZoomed);
    zoomButton.setAttribute("aria-pressed", String(isZoomed));
    zoomButton.textContent = isZoomed ? "−" : "+";
    previousButton.disabled = isZoomed;
    nextButton.disabled = isZoomed;
  };

  const resetZoom = () => {
    setZoom(1, 0, 0);
  };

  const zoomAt = (clientX, clientY, scale) => {
    const stageBounds = imageStage.getBoundingClientRect();
    const pointX = clientX - (stageBounds.left + stageBounds.width / 2);
    const pointY = clientY - (stageBounds.top + stageBounds.height / 2);
    const scaleChange = scale / zoomScale;

    setZoom(
      scale,
      pointX - scaleChange * (pointX - zoomX),
      pointY - scaleChange * (pointY - zoomY),
    );
  };

  const showImage = (index) => {
    currentImage = (index + lightboxLinks.length) % lightboxLinks.length;
    const link = lightboxLinks[currentImage];

    resetZoom();
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
  zoomButton.addEventListener("click", () => {
    if (zoomScale > 1) {
      resetZoom();
    } else {
      const stageBounds = imageStage.getBoundingClientRect();
      zoomAt(
        stageBounds.left + stageBounds.width / 2,
        stageBounds.top + stageBounds.height / 2,
        toggleZoom,
      );
    }
  });

  lightboxImage.addEventListener("click", (event) => {
    if (performance.now() < suppressClickUntil || zoomScale > 1) {
      return;
    }

    const imageBounds = lightboxImage.getBoundingClientRect();
    const step =
      event.clientX < imageBounds.left + imageBounds.width / 2 ? -1 : 1;
    navigate(step);
  });

  const touchDistance = (firstTouch, secondTouch) =>
    Math.hypot(
      secondTouch.clientX - firstTouch.clientX,
      secondTouch.clientY - firstTouch.clientY,
    );

  const touchMidpoint = (firstTouch, secondTouch) => ({
    x: (firstTouch.clientX + secondTouch.clientX) / 2,
    y: (firstTouch.clientY + secondTouch.clientY) / 2,
  });

  const startPinch = (touches) => {
    const midpoint = touchMidpoint(touches[0], touches[1]);
    const stageBounds = imageStage.getBoundingClientRect();

    pinchStart = {
      distance: Math.max(touchDistance(touches[0], touches[1]), 1),
      midpointX: midpoint.x - (stageBounds.left + stageBounds.width / 2),
      midpointY: midpoint.y - (stageBounds.top + stageBounds.height / 2),
      scale: zoomScale,
      x: zoomX,
      y: zoomY,
    };
    gestureStart = null;
    lastTap = null;
  };

  const handleTap = (touch) => {
    const now = performance.now();
    suppressClickUntil = now + 500;

    if (
      lastTap &&
      now - lastTap.time <= 320 &&
      Math.hypot(touch.clientX - lastTap.x, touch.clientY - lastTap.y) <= 32
    ) {
      if (zoomScale > 1) {
        resetZoom();
      } else {
        zoomAt(touch.clientX, touch.clientY, toggleZoom);
      }
      lastTap = null;
    } else {
      lastTap = { time: now, x: touch.clientX, y: touch.clientY };
    }
  };

  lightboxImage.addEventListener(
    "touchstart",
    (event) => {
      if (event.touches.length === 2) {
        event.preventDefault();
        startPinch(event.touches);
      } else if (event.touches.length === 1) {
        pinchStart = null;
        const touch = event.touches[0];
        gestureStart = {
          scale: zoomScale,
          x: touch.clientX,
          y: touch.clientY,
          zoomX,
          zoomY,
          suppressTap: false,
        };
      }
    },
    { passive: false },
  );

  lightboxImage.addEventListener(
    "touchmove",
    (event) => {
      if (event.touches.length === 2) {
        event.preventDefault();
        if (!pinchStart) {
          startPinch(event.touches);
        }

        const midpoint = touchMidpoint(event.touches[0], event.touches[1]);
        const stageBounds = imageStage.getBoundingClientRect();
        const midpointX =
          midpoint.x - (stageBounds.left + stageBounds.width / 2);
        const midpointY =
          midpoint.y - (stageBounds.top + stageBounds.height / 2);
        const scale = clamp(
          (pinchStart.scale *
            touchDistance(event.touches[0], event.touches[1])) /
            pinchStart.distance,
          1,
          maxZoom,
        );
        const scaleChange = scale / pinchStart.scale;

        setZoom(
          scale,
          midpointX - scaleChange * (pinchStart.midpointX - pinchStart.x),
          midpointY - scaleChange * (pinchStart.midpointY - pinchStart.y),
        );
        return;
      }

      if (!gestureStart || event.touches.length !== 1) {
        return;
      }

      const touch = event.touches[0];
      const movementX = touch.clientX - gestureStart.x;
      const movementY = touch.clientY - gestureStart.y;

      if (gestureStart.scale > 1) {
        event.preventDefault();
        setZoom(
          zoomScale,
          gestureStart.zoomX + movementX,
          gestureStart.zoomY + movementY,
        );
      } else if (Math.abs(movementX) > Math.abs(movementY)) {
        event.preventDefault();
      }
    },
    { passive: false },
  );

  lightboxImage.addEventListener("touchend", (event) => {
    if (pinchStart) {
      suppressClickUntil = performance.now() + 500;
      pinchStart = null;

      if (event.touches.length === 1) {
        const touch = event.touches[0];
        gestureStart = {
          scale: zoomScale,
          x: touch.clientX,
          y: touch.clientY,
          zoomX,
          zoomY,
          suppressTap: true,
        };
      } else {
        gestureStart = null;
      }
      return;
    }

    if (!gestureStart || event.changedTouches.length === 0) {
      return;
    }

    const touch = event.changedTouches[0];
    const movementX = touch.clientX - gestureStart.x;
    const movementY = touch.clientY - gestureStart.y;
    const movement = Math.hypot(movementX, movementY);
    const startedZoomed = gestureStart.scale > 1;
    const suppressTap = gestureStart.suppressTap;
    gestureStart = null;

    if (
      !startedZoomed &&
      Math.abs(movementX) >= 45 &&
      Math.abs(movementX) > Math.abs(movementY)
    ) {
      suppressClickUntil = performance.now() + 500;
      lastTap = null;
      navigate(movementX > 0 ? -1 : 1);
    } else if (!suppressTap && movement <= 12) {
      handleTap(touch);
    } else if (movement > 12) {
      suppressClickUntil = performance.now() + 500;
      lastTap = null;
    }
  });

  lightboxImage.addEventListener("touchcancel", () => {
    gestureStart = null;
    pinchStart = null;
    lastTap = null;
  });

  lightboxImage.addEventListener("pointerdown", (event) => {
    if (event.pointerType !== "mouse" || zoomScale <= 1) {
      return;
    }

    event.preventDefault();
    lightboxImage.setPointerCapture(event.pointerId);
    lightbox.classList.add("lightbox--dragging");
    mouseDrag = {
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      zoomX,
      zoomY,
      moved: false,
    };
  });

  lightboxImage.addEventListener("pointermove", (event) => {
    if (!mouseDrag || event.pointerId !== mouseDrag.pointerId) {
      return;
    }

    const movementX = event.clientX - mouseDrag.startX;
    const movementY = event.clientY - mouseDrag.startY;
    mouseDrag.moved ||= Math.hypot(movementX, movementY) > 4;
    setZoom(
      zoomScale,
      mouseDrag.zoomX + movementX,
      mouseDrag.zoomY + movementY,
    );
  });

  const finishMouseDrag = (event) => {
    if (!mouseDrag || event.pointerId !== mouseDrag.pointerId) {
      return;
    }

    if (mouseDrag.moved) {
      suppressClickUntil = performance.now() + 100;
    }
    if (lightboxImage.hasPointerCapture(event.pointerId)) {
      lightboxImage.releasePointerCapture(event.pointerId);
    }
    mouseDrag = null;
    lightbox.classList.remove("lightbox--dragging");
  };

  lightboxImage.addEventListener("pointerup", finishMouseDrag);
  lightboxImage.addEventListener("pointercancel", finishMouseDrag);
  lightboxImage.addEventListener("dragstart", (event) =>
    event.preventDefault(),
  );
  lightboxImage.addEventListener("load", () => {
    setZoom(zoomScale, zoomX, zoomY);
  });

  lightbox.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" && zoomScale === 1) {
      event.preventDefault();
      navigate(-1);
    } else if (event.key === "ArrowRight" && zoomScale === 1) {
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
    resetZoom();
    document.documentElement.classList.remove("lightbox-open");
  });

  window.addEventListener("resize", () => {
    setZoom(zoomScale, zoomX, zoomY);
  });
}
