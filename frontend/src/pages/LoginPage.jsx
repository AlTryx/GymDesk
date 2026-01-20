import { useState } from "react";

export default function LoginPage() {
    const [email, setEmail] = useState("");

    function handleLogin(e) {
        e.preventDefault();
        localStorage.setItem("user_id", 1);
        window.location.href = "/";
    }

    return (
        <div style={{ padding: 40 }}>
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <button type="submit">Login</button>
            </form>
        </div>
    );
}
