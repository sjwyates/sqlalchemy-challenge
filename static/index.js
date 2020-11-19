const myForm = document.getElementById('startStop')

myForm.addEventListener('submit', e => {
    e.preventDefault();
    console.log(form.elements['start'])
    console.log(form.elements['stop'])
})