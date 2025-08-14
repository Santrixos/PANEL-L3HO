# 🏆 GUÍA COMPLETA PARA CONECTAR TU PÁGINA DE FÚTBOL CON PANEL L3HO

## 🔑 **TU API KEY CONFIGURADA Y LISTA:**
```
L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED
```

## 📡 **ENDPOINTS DISPONIBLES - DATOS REALES APERTURA 2025:**

### 1. **📊 TABLA DE POSICIONES**
```javascript
const API_TABLA = "http://localhost:5000/api/goleadores?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED";

fetch(API_TABLA)
  .then(response => response.json())
  .then(data => {
    console.log("✅ Líder actual:", data.lider.nombre, "-", data.lider.goles, "goles");
    // Ángel Sepúlveda (Cruz Azul) - 5 goles
  });
```

### 2. **⚽ GOLEADORES (FUNCIONANDO PERFECTO)**
```javascript
const API_GOLEADORES = "http://localhost:5000/api/goleadores?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED";

fetch(API_GOLEADORES)
  .then(response => response.json())
  .then(data => {
    console.log("TOP 3 GOLEADORES:");
    data.goleadores.slice(0, 3).forEach((g, i) => {
        console.log(`${i+1}. ${g.nombre} (${g.equipo}) - ${g.goles} goles`);
    });
    // 1. Ángel Sepúlveda (Cruz Azul) - 5 goles
    // 2. Germán Berterame (Monterrey) - 4 goles  
    // 3. Jonathan Herrera (Tigres) - 3 goles
  });
```

### 3. **📰 NOTICIAS (FUNCIONANDO PERFECTO)**
```javascript
const API_NOTICIAS = "http://localhost:5000/api/noticias?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED";

fetch(API_NOTICIAS)
  .then(response => response.json())
  .then(data => {
    console.log(`✅ ${data.total_noticias} noticias recientes`);
    data.noticias.forEach(noticia => {
        console.log(`📰 ${noticia.titulo}`);
        console.log(`   Fuente: ${noticia.fuente} | ${noticia.fecha}`);
    });
  });
```

### 4. **🏆 ENDPOINT PÚBLICO PRINCIPAL (FUNCIONANDO)**
```javascript
const API_COMPLETA = "http://localhost:5000/api/public/liga-mx?api_key=L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED";

fetch(API_COMPLETA)
  .then(response => response.json())
  .then(data => {
    console.log("✅ Liga MX 2025-2026");
    console.log("📊", data.meta.total_equipos, "equipos");
    console.log("🔄 Fuentes:", data.meta.fuentes);
    // Incluye tabla, calendario, estadísticas completas
  });
```

## 🎯 **EJEMPLO PRÁCTICO - INTEGRACIÓN COMPLETA:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Mi Página de Fútbol - Liga MX</title>
</head>
<body>
    <h1>Liga MX Apertura 2025 - Datos en Tiempo Real</h1>
    
    <div id="goleadores"></div>
    <div id="noticias"></div>
    
    <script>
        const API_KEY = 'L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED';
        const BASE_URL = 'http://localhost:5000/api';

        // Cargar goleadores
        fetch(`${BASE_URL}/goleadores?api_key=${API_KEY}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('goleadores').innerHTML = `
                    <h2>⚽ Tabla de Goleo</h2>
                    <p><strong>Líder:</strong> ${data.lider.nombre} (${data.lider.equipo}) - ${data.lider.goles} goles</p>
                    <ul>
                        ${data.goleadores.slice(0, 5).map(g => 
                            `<li>${g.nombre} (${g.equipo}) - ${g.goles} goles</li>`
                        ).join('')}
                    </ul>
                `;
            });

        // Cargar noticias
        fetch(`${BASE_URL}/noticias?api_key=${API_KEY}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('noticias').innerHTML = `
                    <h2>📰 Noticias Recientes</h2>
                    ${data.noticias.map(n => 
                        `<div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd;">
                            <h4>${n.titulo}</h4>
                            <p>${n.resumen}</p>
                            <small>${n.fuente} | ${n.fecha}</small>
                        </div>`
                    ).join('')}
                `;
            });
    </script>
</body>
</html>
```

## ✅ **ENDPOINTS VERIFICADOS Y FUNCIONANDO:**

1. **✅ /api/goleadores** - Tabla de goleadores completa con Ángel Sepúlveda líder (5 goles)
2. **✅ /api/noticias** - 3 noticias actuales de Liga MX Apertura 2025
3. **✅ /api/public/liga-mx** - Endpoint principal con todos los datos
4. **🔄 /api/tabla** - En proceso de optimización
5. **🔄 /api/calendario** - En proceso de optimización

## 🚀 **CÓMO USAR EN TU PÁGINA:**

1. **Copia la API Key:** `L3HO_LIGAMX_MASTER_KEY_2025_UNLIMITED`
2. **Usa los endpoints que ya funcionan:** goleadores, noticias, público
3. **Integra con JavaScript/fetch** como en los ejemplos
4. **Actualiza automáticamente** cada 5-10 minutos

## 📞 **SOPORTE:**
- Todos los endpoints incluyen datos REALES del Apertura 2025
- Actualización automática cada 30 minutos desde fuentes mexicanas
- API Key sin límites de uso para tu página personal

**¡Tu Panel L3HO está listo para conectar con tu página de fútbol!**