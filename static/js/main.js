
// ================================
// ON-SCROLL ANIMATIONS
// ================================
document.addEventListener('DOMContentLoaded', () => {
  const animatedElements = document.querySelectorAll('.animate-on-scroll');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target); // Stop observing once visible
      }
    });
  }, { threshold: 0.1 }); // Trigger when 10% of the element is visible
  animatedElements.forEach(el => observer.observe(el));
});

const heroSlider = document.querySelector('.hero.slider');
if (heroSlider) {
  const slides = Array.from(heroSlider.querySelectorAll('.slide'));
  let currentIndex = 0;
  let intervalId = null;

  function showSlide(index) {
    slides.forEach((slide, i) => slide.classList.toggle('is-active', i === index));
  }

  function nextSlide() { currentIndex = (currentIndex + 1) % slides.length; showSlide(currentIndex); }
  function prevSlide() { currentIndex = (currentIndex - 1 + slides.length) % slides.length; showSlide(currentIndex); }

  heroSlider.querySelector('.next')?.addEventListener('click', nextSlide);
  heroSlider.querySelector('.prev')?.addEventListener('click', prevSlide);

  const startAutoplay = () => { if (!intervalId) intervalId = setInterval(nextSlide, 6000); };
  const stopAutoplay = () => { clearInterval(intervalId); intervalId = null; };

  heroSlider.addEventListener('mouseenter', stopAutoplay);
  heroSlider.addEventListener('mouseleave', startAutoplay);

  showSlide(0);
  startAutoplay();
}

document.querySelectorAll('.stat .n').forEach(el=>{
  const target = +el.dataset.to; let n = 0; const step = Math.max(1, Math.floor(target/80));
  const t = setInterval(()=>{ n+=step; if(n>=target){n=target;clearInterval(t);} el.textContent = n; }, 20);
});

async function postJSON(url, data){
  const res = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)});
  return res.json();
}
function wireForm(id, src="website"){
  const f = document.getElementById(id); if(!f) return;
  f.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(f).entries());
    data.consent = !!data.consent; data.source = src;
    const j = await postJSON('/api/leads', data).catch(()=>({ok:false}));
    if(j.ok){ alert('Thanks! We will contact you shortly.'); f.reset(); }
    else { alert('Error: '+(j.error||'Try again.')); }
  });
}
wireForm('quoteForm','quote'); wireForm('contactForm','contact');

function openCalculator(){
  const w = 420, h = 720;
  const y = window.top.outerHeight/2 + window.top.screenY - ( h/2 );
  const x = window.top.outerWidth/2 + window.top.screenX - ( w/2 );
  window.open('/calculator','solarCalc',
    `popup=yes,toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=${w},height=${h},left=${x},top=${y}`);
}

function scrollToQuote() {
  document.getElementById('quote')?.scrollIntoView({ behavior: 'smooth' });
}

// Expose functions to global scope for onclick attributes
window.openCalculator = openCalculator;
window.scrollToQuote = scrollToQuote;

const calcForm = document.getElementById('calcForm');
if(calcForm){
  calcForm.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(calcForm).entries());
    data.bill = parseFloat(data.bill||0);
    data.tariff = parseFloat(data.tariff||8);
    data.sun_hours = parseFloat(data.sun_hours||4.5);
    data.price_per_kw = parseFloat(data.price_per_kw||70000);
    data.subsidy = (parseFloat(data.subsidy||0)/100);
    const out = document.getElementById('calcOut');
    const j = await postJSON('/api/calc', data).catch(()=>({ok:false}));
    if(!j.ok){ out.textContent = 'Please check your inputs.'; return; }
    out.innerHTML = `
      <div class="grid grid-2">
        <div><strong>Recommended Size</strong><br>${j.kw} kW</div>
        <div><strong>Approx Cost (Net)</strong><br>₹ ${j.cost_net.toLocaleString()}</div>
        <div><strong>Gross Cost</strong><br>₹ ${j.cost_gross.toLocaleString()}</div>
        <div><strong>Yearly Savings*</strong><br>₹ ${j.yearly_savings.toLocaleString()}</div>
        <div><strong>Payback</strong><br>${j.payback_years} years</div>
      </div>
      <p class="text-muted">* Indicative; we confirm after site survey.</p>`;
  });
}
