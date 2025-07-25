// 🌀 Animated Count Up
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".stat span").forEach(el => {
    let count = 0;
    const target = +el.getAttribute("data-count");
    const interval = setInterval(() => {
      if (count >= target) {
        clearInterval(interval);
        el.innerText = target;
      } else {
        count += Math.ceil(target / 50);
        el.innerText = count;
      }
    }, 30);
  });

  // 🔄 Testimonials Carousel
  const testimonials = document.querySelectorAll(".testimonial");
  let index = 0;

  setInterval(() => {
    testimonials[index].classList.remove("active");
    index = (index + 1) % testimonials.length;
    testimonials[index].classList.add("active");
  }, 5000);
});
