import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../api/client";

export default function ResourcesPage() {
    const [resources, setResources] = useState([]);
    const [form, setForm] = useState({
        name: "",
        type: "ROOM",
        max_bookings: 1,
        color_code: "#ff0000"
    });

    async function loadResources() {
        const data = await apiGet("/resources/");
        if (data.success) setResources(data.resources);
    }

    async function createResource(e) {
        e.preventDefault();
        const data = await apiPost("/resources/create/", form);
        if (data.success) loadResources();
    }

    useEffect(() => {
        loadResources();
    }, []);

    return (
        <div style={{ padding: 40 }}>
            <h2>Resources</h2>

            <form onSubmit={createResource}>
                <input
                    placeholder="Name"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
                <select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value })}
                >
                    <option value="ROOM">Room</option>
                    <option value="EQUIPMENT">Equipment</option>
                </select>
                <input
                    type="number"
                    value={form.max_bookings}
                    onChange={(e) => setForm({ ...form, max_bookings: +e.target.value })}
                />
                <input
                    type="color"
                    value={form.color_code}
                    onChange={(e) => setForm({ ...form, color_code: e.target.value })}
                />
                <button type="submit">Create</button>
            </form>

            <ul>
                {resources.map(r => (
                    <li key={r.id}>
                        {r.name} ({r.type}) — {r.max_bookings} slots
                    </li>
                ))}
            </ul>
        </div>
    );
}
