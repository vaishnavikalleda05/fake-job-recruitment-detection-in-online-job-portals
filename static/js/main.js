// Active nav link highlight
document.querySelectorAll('.nav-item').forEach(link => {
  if (link.getAttribute('href') === window.location.pathname) {
    link.classList.add('active');
  }
});
