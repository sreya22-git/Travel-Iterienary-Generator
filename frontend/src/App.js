import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:5000";

export default function TravelItineraryGenerator() {
  const [cities, setCities] = useState([]);
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [numDays, setNumDays] = useState("");
  const [itinerary, setItinerary] = useState(null);
  const [error, setError] = useState("");
  const [selectedCostOption, setSelectedCostOption] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/cities`)
      .then((response) => response.json())
      .then((data) => setCities(data))
      .catch((err) => setError("Failed to fetch cities"));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setItinerary(null);
    setSelectedCostOption(null);

    try {
      const response = await fetch(`${API_URL}/generate_itinerary`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ source, destination, num_days: numDays }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate itinerary");
      }

      const data = await response.json();
      setItinerary(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCostOptionSelect = (option) => {
    setSelectedCostOption(option);
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "1rem" }}>
      <h1
        style={{
          fontSize: "1.875rem",
          fontWeight: "bold",
          marginBottom: "1rem",
        }}
      >
        Indian Travel Itinerary Generator
      </h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
        <div style={{ marginBottom: "1rem" }}>
          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", marginBottom: "1rem" }}
          >
            <option value="">Select source city</option>
            {cities.map((city) => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <select
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", marginBottom: "1rem" }}
          >
            <option value="">Select destination city</option>
            {cities.map((city) => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <input
            type="number"
            placeholder="Number of days"
            value={numDays}
            onChange={(e) => setNumDays(e.target.value)}
            min="1"
            style={{ width: "100%", padding: "0.5rem", marginBottom: "1rem" }}
          />
        </div>
        <button
          type="submit"
          style={{
            backgroundColor: "#4CAF50",
            border: "none",
            color: "white",
            padding: "15px 32px",
            textAlign: "center",
            textDecoration: "none",
            display: "inline-block",
            fontSize: "16px",
            margin: "4px 2px",
            cursor: "pointer",
          }}
        >
          Generate Itinerary
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {itinerary && (
        <div>
          <h2
            style={{
              fontSize: "1.5rem",
              fontWeight: "bold",
              marginBottom: "1rem",
            }}
          >
            Estimated Costs
          </h2>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "1rem",
            }}
          >
            {Object.entries(itinerary.estimated_costs).map(([option, cost]) => (
              <button
                key={option}
                onClick={() => handleCostOptionSelect(option)}
                style={{
                  padding: "0.5rem 1rem",
                  backgroundColor:
                    selectedCostOption === option ? "#4CAF50" : "#f0f0f0",
                  color: selectedCostOption === option ? "white" : "black",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                {option.charAt(0).toUpperCase() + option.slice(1)} Option: ₹
                {cost}
              </button>
            ))}
          </div>

          <h2
            style={{
              fontSize: "1.5rem",
              fontWeight: "bold",
              marginBottom: "1rem",
            }}
          >
            Your Travel Itinerary
          </h2>
          {selectedCostOption ? (
            itinerary.itinerary[selectedCostOption].map((day) => (
              <div
                key={day.day}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                  padding: "1rem",
                  marginBottom: "1rem",
                }}
              >
                <h3
                  style={{
                    fontSize: "1.25rem",
                    fontWeight: "semibold",
                    marginBottom: "0.5rem",
                  }}
                >
                  Day {day.day} - {day.date}
                </h3>
                <div>
                  <p>
                    <strong>Activities:</strong> {day.activities.join(", ")}
                  </p>
                  <p>
                    <strong>Hotel:</strong> {day.hotel}
                  </p>
                  <p>
                    <strong>Restaurant:</strong> {day.restaurant}
                  </p>
                  <p>
                    <strong>Transport:</strong> {day.transport}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <p>Please select a cost option to view the itinerary.</p>
          )}
        </div>
      )}
    </div>
  );
}
