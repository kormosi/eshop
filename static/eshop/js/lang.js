const STORAGE_KEY = 'lang';

function setLang(lang) {

    localStorage.setItem(STORAGE_KEY, lang);

    document.querySelectorAll('.lang').forEach(el => {
        el.classList.toggle('active', el.id === lang + '-content' || el.id === lang + '-nav');
    });

    document.querySelectorAll('.lang-switch a').forEach(a => {
        a.classList.toggle('active', a.id === lang);
    });

}

const initialLang = localStorage.getItem(STORAGE_KEY) || 'sk';
setLang(initialLang);

document.querySelectorAll('.lang-switch a').forEach(a => a.addEventListener('click', () => setLang(a.id)));
