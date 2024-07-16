import { useState } from "react";
import api from "../api";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import { useNavigate, Link } from "react-router-dom";
import "../styles/Form.css";
import LoadingIndicator from "./LoadingIndicator";

const Form = ({ route, method }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const formName = method == "login" ? "Login" : "Register";

  const handleSubmit = async (e) => {
    setLoading(true);
    e.preventDefault();
    try {
      console.log("About to send POST request..");
      const res = await api.post(route, {
        username,
        password,
      });
      if (method == "login") {
        console.log("Got inside conditional");
        // console.log("ACCESS data: ", res.data.access);
        // console.log("REFRESH data: ", res.data.refresh);
        // localStorage.setItem(ACCESS_TOKEN, res.data.access);
        // localStorage.setItem(REFRESH_TOKEN, res.data.refresh);

        try {
          localStorage.setItem(ACCESS_TOKEN, res.data.access);
          localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
          console.log("Tokens saved to localStorage");
        } catch (storageError) {
          console.error("Error saving tokens to localStorage:", storageError);
        }

        try {
          navigate("/");
          console.log("Navigation to home");
        } catch (navError) {
          console.error("Error during navigation:", navError);
        }
        // navigate("/");
      } else {
        // if register immediately redirect to login page
        navigate("/login");
      }
    } catch (error) {
      console.log("Current route: ", route);
      console.error(
        "Error:",
        error.response ? error.response.data : error.message
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-container">
      <h1>{formName}</h1>
      <input
        className="form-input"
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        className="form-input"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      {loading && <LoadingIndicator />}
      <button className="form-button" type="submit">
        {formName}
      </button>
      {formName == "Login" ? (
        <Link to="/register" className="form-link">
          <p className="form-text">No account? Register now!</p>
        </Link>
      ) : (
        ""
      )}
    </form>
  );
};

export default Form;
