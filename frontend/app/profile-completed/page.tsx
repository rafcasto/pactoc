'use client';

import React from 'react';
import { CheckCircle, Mail, Clock } from 'lucide-react';

export default function ProfileCompleted() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-6" />
        
        <h1 className="text-2xl font-light text-gray-900 mb-4">
          ¡Perfil Completado!
        </h1>
        
        <p className="text-gray-600 mb-6">
          Tu información ha sido registrada exitosamente. 
          Tu nutricionista revisará tu perfil y te enviará tu plan personalizado pronto.
        </p>
        
        <div className="space-y-4 text-left bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <Clock className="w-5 h-5 text-blue-500 mt-0.5" />
            <div>
              <p className="font-medium text-gray-900 text-sm">Tiempo estimado</p>
              <p className="text-gray-600 text-sm">24-48 horas hábiles</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <Mail className="w-5 h-5 text-blue-500 mt-0.5" />
            <div>
              <p className="font-medium text-gray-900 text-sm">Notificación</p>
              <p className="text-gray-600 text-sm">Recibirás un email cuando tu plan esté listo</p>
            </div>
          </div>
        </div>
        
        <p className="text-sm text-gray-500">
          Si tienes preguntas, puedes contactar directamente con tu nutricionista.
        </p>
      </div>
    </div>
  );
}
