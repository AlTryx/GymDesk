import { useState, useEffect, useCallback } from "react";
import { apiGet, apiPost } from "../api/client";

export default function ReservationsPage() {
    const user_id = localStorage.getItem("user_id");
    const [reservations, setReservations] = useState([]);

    const loadReservations = useCallback(async () => {
        const data = await apiGet(`/reservations/user/${user_id}/`);
        if (data.success) setReservations(data.reservations);
    }, [user_id]);

    async function cancel(id) {
        await apiPost(`/reservations/${id}/cancel/`, { user_id });
        loadReservations();
    }

    useEffect(() => {
        loadReservations();
    }, [loadReservations]);

    return (
        <div style={{ padding: 40 }}>
            <h2>Your Reservations</h2>

            <ul>
                {reservations.map(r => (
                    <li key={r.id}>
                        Reservation #{r.id} — status: {r.status}
                        <button onClick={() => cancel(r.id)}>
                            Cancel
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}