const STORAGE_KEY = 'lang';

function setLang(lang) {

    document.querySelectorAll('.lang').forEach(el => {
        el.classList.toggle('active', el.id === lang + '-content' || el.id === lang + '-nav');
    });

    document.querySelectorAll('.lang-switch a').forEach(a => {
        a.classList.toggle('active', a.id === lang);
    });

}

// lang switch is hidden in base.html: force Slovak so visitors who picked EN aren't stuck
// restore when the switch comes back: const initialLang = localStorage.getItem(STORAGE_KEY) || 'sk';
const initialLang = 'sk';
setLang(initialLang);

document.querySelectorAll('.lang-switch a').forEach(a => a.addEventListener('click', () => {
    localStorage.setItem(STORAGE_KEY, a.id);
    setLang(a.id);
}));
