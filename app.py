import ddf.minim.*; 
import processing.serial.*;
import mqtt.*;

MQTTClient client;
float t = 0, h = 0;
String estado = "";

// Imágenes de bebé
PImage bebeFrio, bebeCalor, bebeFeliz;

// Audios
Minim minim;
AudioPlayer frioAudio, calorAudio, estableAudio;

void setup() {
  size(800, 600);
  
  // MQTT
  client = new MQTTClient(this);
  client.connect("mqtt://test.mosquitto.org", "processingClient");
  client.subscribe("sensor/temperatura");

  // Cargar imágenes
  bebeFrio = loadImage("bebeFrio.png");
  bebeCalor = loadImage("bebeCalor.png");
  bebeFeliz = loadImage("bebeFeliz.png");
  
  // Cargar audios
  minim = new Minim(this);
  frioAudio = minim.loadFile("frio.mp3");
  calorAudio = minim.loadFile("calor.mp3");
  estableAudio = minim.loadFile("estable.mp3");
}

void draw() {
  // Fondo y estado
  if (t < 18) {
    background(150, 200, 255);  // Azul pastel
    image(bebeFrio, 200, 150, 400, 400);
    estado = "El cuarto está demasiado frío ❄️";
  } else if (t > 28) {
    background(255, 240, 150);  // Amarillo pastel
    image(bebeCalor, 200, 150, 400, 400);
    estado = "El cuarto está demasiado caliente ☀️";
  } else {
    background(255, 255, 255);  // Blanco
    image(bebeFeliz, 200, 150, 400, 400);
    estado = "El clima está bien 😊";
  }
  
  fill(50);
  textSize(28);
  text("Temperatura: " + nf(t, 1, 1) + " °C", 50, 60);
  text("Humedad: " + nf(h, 1, 1) + " %", 50, 100);
  text(estado, 50, 150);
}

void messageReceived(String topic, byte[] payload) {
  String msg = new String(payload);
  JSONObject j = parseJSONObject(msg);
  if (j != null) {
    t = j.getFloat("t");
    h = j.getFloat("h");
    
    // Reproducir audio según estado
    if (t < 18) {
      frioAudio.rewind();
      frioAudio.play();
    } else if (t > 28) {
      calorAudio.rewind();
      calorAudio.play();
    } else {
      estableAudio.rewind();
      estableAudio.play();
    }
  }
}


