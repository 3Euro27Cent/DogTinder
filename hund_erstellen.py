{% extends "base.html" %}

{% block title %}Hunde Profil{% endblock %}

{% block additional_styles %}
<style>
    .dog-profile-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        padding: 20px;
        margin-top: 20px;
    }

    .dog-profile-form {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        width: 100%;
        max-width: 600px;
    }

    .form-section {
        margin: 20px 0;
    }

    .form-section label {
        font-size: 1.2rem;
        color: #333;
    }

    .form-section input,
    .form-section select {
        padding: 10px;
        margin: 5px 0;
        width: 100%;
        border-radius: 5px;
        border: 1px solid #ddd;
        font-size: 1rem;
    }

    .form-section button {
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        font-size: 1.2rem;
        cursor: pointer;
        border: none;
    }

    .form-section button:hover {
        background-color: #2196F3;
    }

    .dog-image-preview {
        display: flex;
        justify-content: center;
        margin: 20px;
    }

    .dog-image-preview img {
        width: 1024px;
        height: 1536px;
        object-fit: cover;
        border-radius: 10px;
    }

    .crop-button {
        margin-top: 10px;
        padding: 8px 16px;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        cursor: pointer;
    }

    .crop-button:hover {
        background-color: #2196F3;
    }
</style>
{% endblock %}

{% block content %}
<div class="dog-profile-container">
    <h1>Erstelle einen Hund</h1>
    <form class="dog-profile-form" method="POST" enctype="multipart/form-data">
        <div class="form-section">
            <label for="name">Name des Hundes:</label>
            <input type="text" name="name" id="name" required>
        </div>
        <div class="form-section">
            <label for="description">Beschreibung:</label>
            <textarea name="description" id="description" required></textarea>
        </div>
        <div class="form-section">
            <label for="image">Bild hochladen (1024x1536):</label>
            <input type="file" name="image" id="image" accept="image/*" required>
        </div>
        <div class="form-section">
            <label for="rasse">Rasse:</label>
            <input type="text" name="rasse" id="rasse" required>
        </div>
        <div class="form-section">
            <label for="alter">Alter:</label>
            <input type="number" name="alter" id="alter" required>
        </div>
        <div class="form-section">
            <label for="geschlecht">Geschlecht:</label>
            <select name="geschlecht" id="geschlecht">
                <option value="weiblich">Weiblich</option>
                <option value="männlich">Männlich</option>
            </select>
        </div>
        <div class="form-section">
            <label for="groesse">Größe:</label>
            <select name="groesse" id="groesse">
                <option value="klein">Klein</option>
                <option value="mittel">Mittel</option>
                <option value="groß">Groß</option>
            </select>
        </div>
        <div class="form-section">
            <label for="gewicht">Gewicht (kg):</label>
            <input type="number" name="gewicht" id="gewicht" required>
        </div>
        <div class="form-section">
            <label for="geimpft">Geimpft:</label>
            <input type="checkbox" name="geimpft" id="geimpft">
        </div>
        <div class="form-section">
            <label for="kastriert">Kastriert:</label>
            <input type="checkbox" name="kastriert" id="kastriert">
        </div>
        <div class="form-section">
            <label for="kinderfreundlich">Kinderfreundlich:</label>
            <input type="checkbox" name="kinderfreundlich" id="kinderfreundlich">
        </div>
        <div class="form-section">
            <label for="hundevertraeglich">Verträglich mit anderen Hunden:</label>
            <input type="checkbox" name="hundevertraeglich" id="hundevertraeglich">
        </div>
        <div class="form-section">
            <label for="aktivitaetslevel">Aktivitätslevel:</label>
            <select name="aktivitaetslevel" id="aktivitaetslevel">
                <option value="ruhig">Ruhig</option>
                <option value="ausgeglichen">Ausgeglichen</option>
                <option value="aktiv">Aktiv</option>
            </select>
        </div>

        <div class="dog-image-preview">
            <img id="image-preview" src="#" alt="Image Preview" style="display: none;">
        </div>

        <div class="form-section">
            <button type="submit">Hund erstellen</button>
        </div>
    </form>
</div>

<script>
    const imageInput = document.getElementById("image");
    const imagePreview = document.getElementById("image-preview");

    imageInput.addEventListener("change", function(event) {
        const file = event.target.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = "block";
        };
        reader.readAsDataURL(file);
    });
</script>
{% endblock %}

