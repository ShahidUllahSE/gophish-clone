const closeBtn = document.getElementById('close');
const modalMenu = document.getElementById('modal');
const modalBtn = document.querySelector('.modal__button');

setTimeout(()=>{
  modalMenu.classList.add('show');
},3000);

closeBtn.addEventListener('click',()=>{modalMenu.classList.remove('show')});
modalBtn.addEventListener('click',()=>{modalMenu.classList.remove('show')});