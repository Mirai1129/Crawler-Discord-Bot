const cards = document.querySelectorAll(".card-body");

cards.forEach((card) => {
    card.addEventListener("mousemove", (e) => {
        let cardInnerHeight = card.clientHeight;
        let cardInnerWidth = card.clientWidth;

        //console.log("Inner Height: " + cardInnerHeight);
        //console.log("Inner Width: " + cardInnerWidth);
        let rect = card.getBoundingClientRect();
        let cardXposition=e.clientX - rect.left;
        let cardYposition=e.clientY - rect.top;
        
        let rotateSpeed=40;

        let xCustom=2.5;
        let yCustom=1.25;

        let x=(cardInnerHeight/xCustom - cardXposition)/rotateSpeed;
        let y=(cardInnerWidth/yCustom - cardYposition)/rotateSpeed;

        card.style.transform="rotate("+x+"deg) rotateX("+y+"deg)";
    });
    //調整晃動
    const cardFigure=card.querySelector(".card-figure");
    const cardName=card.querySelector(".card-name");
    const cardDescription=card.querySelector(".card-description");
    const cardDescription2=card.querySelector(".card-description2");
    const cardMedia=card.querySelector(".card-media")
    //滑鼠進
    card.addEventListener("mouseover",()=>{
        cardFigure.style.transform="translate3d(0,0,150px)";
        cardName.style.transform="translate3d(0,0,180px)";
        cardDescription.style.transform="translate3d(0,0,190px)";
        cardDescription2.style.transform="translate3d(0,0,190px)";
        cardMedia.style.transform="translate3d(0,0,140px)";
        card.style.transform="none"
    });
    //滑鼠離開
    card.addEventListener("mouseout",()=>{
        cardFigure.style.transform="translate3d(0,0,0)";
        cardName.style.transform="translate3d(0,0,0)";
        cardDescription.style.transform="translate3d(0,0,0)";
        cardDescription2.style.transform="translate3d(0,0,0)";
        cardMedia.style.transform="translate3d(0,0,0)";
        card.style.transform="rotateY(0deg) rotateX(0deg)";
        card.style.transform="transform .5s ease"
    })
});


