#!/bin/bash
# Script para iniciar el Sistema de Recetas Dietéticas completo

echo "🚀 SISTEMA DE RECETAS DIETÉTICAS"
echo "================================="
echo "🥗 Sistema completo de recetas personalizadas"
echo "🔄 Iniciando backend y frontend..."
echo ""

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo Sistema de Recetas Dietéticas..."
    pkill -f "python.*final_backend_server" 2>/dev/null
    pkill -f "next dev" 2>/dev/null
    echo "✅ Servicios detenidos"
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGINT SIGTERM

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/run_diet_server.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Ejecutar desde el directorio raíz del proyecto (pactoc/)"
    echo "💡 Asegúrate de estar en el directorio pactoc/"
    exit 1
fi

# Limpiar procesos previos
echo "🧹 Limpiando procesos previos..."
pkill -f "python.*server" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 2

# Validar enums antes de iniciar
echo "🔍 Validando configuración de base de datos..."
cd backend
if ./venv/bin/python scripts/quick_enum_fix.py > /dev/null 2>&1; then
    echo "✅ Base de datos validada"
else
    echo "⚠️  Ejecutando corrección automática de enums..."
    ./venv/bin/python scripts/quick_enum_fix.py
fi
cd ..

echo "🔧 Iniciando Backend del Sistema de Recetas (Puerto 8000)..."
cd backend
python3.11 run_diet_server.py > server.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "⏳ Esperando que el backend inicie..."
sleep 5

# Verificar que el backend esté ejecutándose (verificar el proceso)
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend iniciado correctamente en http://localhost:8000"
    echo "🔍 Probando endpoint: curl -s http://localhost:8000/"
else
    echo "❌ Error: Backend no se inició correctamente"
    echo "🔍 Verificando logs..."
    tail -10 backend/server.log 2>/dev/null || echo "No se pudo leer server.log"
    exit 1
fi

echo ""
echo "🎨 Iniciando Frontend (Puerto 3000)..."
cd frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "⏳ Esperando que el frontend inicie..."
sleep 5

echo ""
echo "🎉 SISTEMA DE RECETAS DIETÉTICAS INICIADO"
echo "========================================"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo ""
echo "🔗 URLS PARA PROBAR:"
echo "📋 Formulario del Paciente:"
echo "   http://localhost:3000/complete-profile/QizKtpixpDYa6_UwgWgW54Rh0GcTUO2x8oblSAloT-E"
echo ""
echo "🧪 API Endpoints:"
echo "   curl http://localhost:8000/api/public/catalogs"
echo "   curl http://localhost:8000/api/public/invitations/QizKtpixpDYa6_UwgWgW54Rh0GcTUO2x8oblSAloT-E"
echo ""
echo "📊 Sistema: Recetas Dietéticas Personalizadas"
echo "🆔 Backend PID: $BACKEND_PID"
echo "🆔 Frontend PID: $FRONTEND_PID"
echo ""
echo "⚡ Presiona Ctrl+C para detener ambos servicios"

# Mantener el script ejecutándose
while true; do
    sleep 10
    # Verificar que los servicios sigan ejecutándose
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend se detuvo inesperadamente"
        cleanup
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend se detuvo inesperadamente"
        cleanup
    fi
done
