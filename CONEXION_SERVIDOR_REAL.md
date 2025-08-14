# 🌐 CONEXIÓN CON SERVIDOR REAL - Panel L3HO

## 🔗 **URL DE TU SERVIDOR:**
```
https://servidorl3ho.replit.app
```

## 🔑 **API KEY CONFIGURADA:**
```
L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED
```

## 📡 **ENDPOINTS LISTOS PARA TU PÁGINA:**

### 1. **⚽ GOLEADORES (FUNCIONANDO)**
```javascript
const API_GOLEADORES = "https://servidorl3ho.replit.app/api/goleadores?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED";

fetch(API_GOLEADORES)
  .then(response => response.json())
  .then(data => {
    console.log("Líder:", data.lider.nombre, "-", data.lider.goles, "goles");
    // Ángel Sepúlveda (Cruz Azul) - 5 goles
  });
```

### 2. **📰 NOTICIAS (FUNCIONANDO)**
```javascript
const API_NOTICIAS = "https://servidorl3ho.replit.app/api/noticias?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED";

fetch(API_NOTICIAS)
  .then(response => response.json())
  .then(data => {
    console.log("Noticias:", data.total_noticias, "disponibles");
    data.noticias.forEach(n => console.log("📰", n.titulo));
  });
```

### 3. **🏆 ENDPOINT PÚBLICO COMPLETO (FUNCIONANDO)**
```javascript
const API_COMPLETA = "https://servidorl3ho.replit.app/api/public/liga-mx?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED";

fetch(API_COMPLETA)
  .then(response => response.json())
  .then(data => {
    console.log("Liga:", data.liga, data.temporada);
    console.log("Equipos:", data.meta.total_equipos);
    console.log("Fuentes:", data.meta.fuentes);
  });
```

## 🎯 **CÓDIGO PARA COPIAR Y PEGAR EN TU PÁGINA:**

```html
<script>
// Configuración para tu servidor real
const API_BASE = 'https://servidorl3ho.replit.app/api';
const API_KEY = 'L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED';

// Función para obtener goleadores
async function obtenerGoleadores() {
    try {
        const response = await fetch(`${API_BASE}/goleadores?api_key=${API_KEY}`);
        const data = await response.json();
        
        console.log("✅ Líder de goleo:", data.lider.nombre, "-", data.lider.goles, "goles");
        
        // Mostrar en tu página
        document.getElementById('goleadores').innerHTML = `
            <h3>⚽ Tabla de Goleo</h3>
            <p><strong>Líder:</strong> ${data.lider.nombre} (${data.lider.equipo}) - ${data.lider.goles} goles</p>
            <ul>
                ${data.goleadores.slice(0, 5).map(g => 
                    `<li>${g.nombre} (${g.equipo}) - ${g.goles} goles</li>`
                ).join('')}
            </ul>
        `;
    } catch (error) {
        console.error("❌ Error:", error);
    }
}

// Función para obtener noticias
async function obtenerNoticias() {
    try {
        const response = await fetch(`${API_BASE}/noticias?api_key=${API_KEY}`);
        const data = await response.json();
        
        console.log("✅ Noticias:", data.total_noticias, "disponibles");
        
        // Mostrar en tu página
        document.getElementById('noticias').innerHTML = `
            <h3>📰 Noticias Liga MX</h3>
            ${data.noticias.map(n => `
                <div style="margin: 10px 0; padding: 10px; border-left: 3px solid #007bff;">
                    <h4>${n.titulo}</h4>
                    <p>${n.resumen}</p>
                    <small>${n.fuente} | ${n.fecha}</small>
                </div>
            `).join('')}
        `;
    } catch (error) {
        console.error("❌ Error:", error);
    }
}

// Cargar datos al iniciar
obtenerGoleadores();
obtenerNoticias();

// Auto-actualizar cada 10 minutos
setInterval(() => {
    obtenerGoleadores();
    obtenerNoticias();
}, 600000);
</script>

<!-- HTML básico para mostrar datos -->
<div id="goleadores">Cargando goleadores...</div>
<div id="noticias">Cargando noticias...</div>
```

## 🔄 **URLS DIRECTAS PARA PROBAR:**

1. **Goleadores:**
   ```
   https://servidorl3ho.replit.app/api/goleadores?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED
   ```

2. **Noticias:**
   ```
   https://servidorl3ho.replit.app/api/noticias?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED
   ```

3. **API Completa:**
   ```
   https://servidorl3ho.replit.app/api/public/liga-mx?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED
   ```

## ✅ **DATOS REALES DISPONIBLES:**

- **Líder de Goleo:** Ángel Sepúlveda (Cruz Azul) - 5 goles
- **Temporada:** Apertura 2025, Jornada 4
- **Fuentes:** ESPN México, Mediotiempo, Liga MX Oficial
- **Actualización:** Automática cada 30 minutos
- **Sin límites:** API Key sin restricciones para tu uso personal

## 🚀 **INSTRUCCIONES:**

1. Copia el archivo `ejemplo_conexion_api_servidor.html`
2. Abre en tu navegador para ver la demo funcionando
3. Usa el código JavaScript en tu propia página
4. Las URLs funcionan directamente desde tu servidor de Replit

**¡Tu API de Liga MX está lista para usar desde cualquier página web!**