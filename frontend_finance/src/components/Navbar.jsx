import { useState, useEffect } from "react";
import "../styles/Navbar.css";

const Navbar = () => {
  const [username, setUsername] = useState("");

  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    }
  }, []);

  return (
    <div className="nb-container">
      <h2 className="nb-content">Welcome Back {username}!</h2>
      <p className="nb-content">ICON</p>
    </div>
  );
};

export default Navbar;
