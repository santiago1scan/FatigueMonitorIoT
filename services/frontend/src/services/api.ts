/**
 * API Service - Comunicación con el backend
 *
 * Responsabilidad única: Gestionar llamadas HTTP a la API REST.
 * Abstrae los detalles de comunicación HTTP para que los componentes
 * solo conozcan interfaces de dominio.
 */

import { ApiResponse, API_BASE_URL } from "@/types/index";

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Inicia el sistema de asistencia
   * POST /assist/start
   */
  async startAssist(): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/assist/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Detiene el sistema de asistencia
   * POST /assist/stop
   */
  async stopAssist(): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}/assist/stop`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();
