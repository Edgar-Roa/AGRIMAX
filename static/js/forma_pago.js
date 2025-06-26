document.addEventListener('click',e=>{
    const m=document.getElementById("menuContent");
    const b=document.querySelector(".menu-button");
    if(m.style.display==='block'&&!m.contains(e.target)&&!b.contains(e.target)){
        m.style.display='none';
    }
});