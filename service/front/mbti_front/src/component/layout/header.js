import React from "react";
import "./header.css"

const Header = (props) => {
    return (
        <header className="header" >
            <div className="bar"/>
            <div className="img_wrapper">
              <img className="head_img" alt="headerimg" src="img/title.png" onClick={() => props.setMode("MAIN")}/>
              <img className="head_img2" alt="headerimg" src="img/title2.png"/>
            </div>           
        </header>
    )
}

export default Header