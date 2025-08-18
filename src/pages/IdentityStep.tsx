import { useState } from "react";
import "./IdentityStep.css";

interface Props { 
  next: (role: "teacher" | "student") => void 
}

export default function IdentityStep({ next }: Props) {
  const [selectedRole, setSelectedRole] = useState<"teacher" | "student">("student");

  const handleNext = () => {
    next(selectedRole);
  };

  return (
    <div className="identity-container">
      <h2 className="identity-title">選擇身分</h2>
      
      <div className="select-wrapper">
        <select 
          className="role-select"
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value as "teacher" | "student")}
        >
          <option value="student">學生</option>
          <option value="teacher">教師</option>
        </select>
      </div>

      <button className="next-button" onClick={handleNext}>
        <span>下一步</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  );
}
