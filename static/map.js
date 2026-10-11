const map = L.map("location-map").setView([34.258333, 108.928611], 3);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let locationRequestVersion = 0;
async function onMapClick(event) {
    const requestVersion = ++locationRequestVersion;
    const coordinates = event.latlng.wrap();
    const latitude = coordinates.lat;
    const longitude = coordinates.lng;
    console.log("Latitude:", latitude, "Longitude:", longitude);

    const suggestions = document.getElementById("location-suggestions");
    suggestions.replaceChildren();

    const response = await fetch("/api/location", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        })
    });
    const locationOptions = await response.json();
    if (requestVersion !== locationRequestVersion) {
    return;
    }
    console.log(locationOptions)

    if (!response.ok) {
        console.error(locationOptions.error);
        return;
    }

    for (const option of locationOptions) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = option.name;

        button.addEventListener("click", function(){
            const LocationInput = document.getElementById("locations");
            LocationInput.value = option.name;
            document.getElementById("location-id").value = option.id;
            document.getElementById("location-type").value = option.type;
            document.getElementById("location-country-id").value = option.country_id;
            suggestions.replaceChildren();
        });

        suggestions.appendChild(button);
    }






}

map.on("click", onMapClick);