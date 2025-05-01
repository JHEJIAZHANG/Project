import React from 'react';
import { FaSmile } from "react-icons/fa";
import LoginForm from '../components/LoginForm';
import '../styles/LoginForm.css';

function Login() {
  return (
    <div className="login-page">
      <div className="logo-container">
        <span className="logo-text">
            <FaSmile className="logo-icon" /> Social
        </span>
      </div>
      <LoginForm />
    </div>
  );
}

export default Login;