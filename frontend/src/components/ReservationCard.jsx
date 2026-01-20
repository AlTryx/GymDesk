export default function ReservationCard({ reservation, onCancel }) {
    return (
        <div style={{
            border: "1px solid #ccc",
            padding: 10,
            borderRadius: 8,
            marginBottom: 10
        }}>
            <p>ID: {reservation.id}</p>
            <p>Status: {reservation.status}</p>

            <button onClick={onCancel}>
                Cancel
            </button>
        </div>
    );
}
