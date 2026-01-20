import { Link } from "react-router-dom";

export default function Navbar() {
    return (
        <nav style={{ padding: "10px", background: "#222", color: "#fff" }}>
            <Link to="/" style={{ marginRight: 15 }}>Dashboard</Link>
            <Link to="/reservations" style={{ marginRight: 15 }}>Reservations</Link>
            <Link to="/resources">Resources</Link>
        </nav>
    );
}
