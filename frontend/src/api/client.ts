// API Client for GymDesk Django Backend
const API_BASE_URL = "http://localhost:8000/api";

// Types based on Django serializers
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'User' | 'Admin';
  created_at: string | null;
}

export interface Resource {
  id: number;
  name: string;
  type: 'Room' | 'Equipment';
  max_bookings: number;
  color_code: string;
  created_at: string | null;
}

export interface TimeSlot {
  id: number;
  resource_id: number;
  start_time: string;
  end_time: string;
  is_available: boolean;
  duration_minutes: number;
}

export interface Reservation {
  id: number;
  user_id: number;
  resource_id: number;
  time_slot_id: number;
  status: 'Active' | 'Cancelled';
  notes: string | null;
  created_at: string | null;
}

interface ApiResponse<T> {
  success: boolean;
  error?: string;
  [key: string]: T | boolean | string | undefined;
}

// Generic fetch wrapper
type ApiRequestOptions = RequestInit & { skipAuth?: boolean };

async function apiRequest<T = any>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // attach Authorization header if token exists and caller didn't opt-out
  const token = !options.skipAuth ? getAccessToken() : null;
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {};

  // clone headers but avoid sending skipAuth to fetch
  const { skipAuth, ...fetchOptions } = options as any;

  // perform fetch with optional token override
  const doFetch = async (tokenOverride: string | null) => {
    const hdrToken = tokenOverride ?? (!skipAuth ? getAccessToken() : null);
    const hdr = hdrToken ? { Authorization: `Bearer ${hdrToken}` } : {};
    return fetch(url, {
      ...fetchOptions,
      headers: {
        'Content-Type': 'application/json',
        ...hdr,
        ...((fetchOptions && fetchOptions.headers) || {}),
      },
    });
  };

  let response = await doFetch(token);

  // If unauthorized and we're using auth, try refreshing once and retry.
  if (response.status === 401 && !skipAuth) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      const newToken = getAccessToken();
      response = await doFetch(newToken);
    }
  }

  // Read response body safely (may be empty or non-json)
  const text = await response.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (e) {
    data = null;
  }

  // If HTTP status indicates error, prefer server message fields or statusText
  if (!response.ok) {
    const errMsg = (data && (data.error || data.detail || data.message)) || response.statusText || `HTTP ${response.status}`;
    throw new Error(errMsg || 'Грешка при заявката');
  }

  // At this point response is ok. Some endpoints follow { success: true, ... }.
  if (data && Object.prototype.hasOwnProperty.call(data, 'success') && data.success === false) {
    const errMsg = data.error || data.detail || data.message || 'Грешка при заявката';
    throw new Error(errMsg);
  }

  // If data is null (no body), return an empty object
  return (data ?? {}) as T;
}

// Token helpers
export function setAccessToken(token: string | null) {
  if (token) localStorage.setItem('gd_access', token);
  else localStorage.removeItem('gd_access');
}

export function getAccessToken(): string | null {
  return localStorage.getItem('gd_access');
}

export function setCurrentUserId(id: number | null) {
  if (id !== null) localStorage.setItem('gd_user_id', String(id));
  else localStorage.removeItem('gd_user_id');
}

export function getCurrentUserId(): number | null {
  const v = localStorage.getItem('gd_user_id');
  return v ? parseInt(v, 10) : null;
}

export function setCurrentUserRole(role: string | null) {
  if (role) localStorage.setItem('gd_user_role', role);
  else localStorage.removeItem('gd_user_role');
}

export function getCurrentUserRole(): string | null {
  return localStorage.getItem('gd_user_role');
}

export function setRefreshToken(token: string | null) {
  if (token) localStorage.setItem('gd_refresh', token);
  else localStorage.removeItem('gd_refresh');
}

export function getRefreshToken(): string | null {
  return localStorage.getItem('gd_refresh');
}

// Auth API
export const authApi = {
  login: async (data: { email: string; password: string }) => {
    const res = await apiRequest('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true,
    });
    // store access token
    if (res.access) setAccessToken(res.access as string);
    if (res.refresh) setRefreshToken(res.refresh as string);
    if (res.user_id) setCurrentUserId(res.user_id as number);
    if (res.role) setCurrentUserRole(res.role as string);
    return res;
  },

  register: async (data: { email: string; username: string; password: string }) => {
    const res = await apiRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true,
    });
    if (res.access) setAccessToken(res.access as string);
    if (res.refresh) setRefreshToken(res.refresh as string);
    if (res.user_id) setCurrentUserId(res.user_id as number);
    if (res.role) setCurrentUserRole(res.role as string);
    return res;
  },
};

// Try to refresh access token using the stored refresh token.
async function refreshAccessToken(): Promise<boolean> {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  const url = `${API_BASE_URL}/auth/refresh/`;
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    const text = await resp.text();
    const data = text ? JSON.parse(text) : null;
    if (!resp.ok) {
      // Clear tokens on failed refresh
      setAccessToken(null);
      setRefreshToken(null);
      setCurrentUserId(null);
      return false;
    }

    if (data && data.access) {
      setAccessToken(data.access as string);
      return true;
    }
    return false;
  } catch (err) {
    setAccessToken(null);
    setRefreshToken(null);
    setCurrentUserId(null);
    return false;
  }
}

// Reservations API
export const reservationsApi = {
  create: async (data: {
    resource_id: number;
    timeslot_id: number;
    notes?: string;
  }): Promise<{ success: boolean; reservation: Reservation }> => {
    const res = await apiRequest('/reservations/create/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (res.reservation && typeof res.reservation.status === 'string') {
      res.reservation.status = res.reservation.status === 'ACTIVE' ? 'Active' : 'Cancelled';
    }

    return res;
  },

  list: async (status?: string): Promise<{ success: boolean; reservations: Reservation[] }> => {
    const params = status ? `?status=${status}` : '';
    const res = await apiRequest(`/reservations/${params}`);
    if (res.reservations && Array.isArray(res.reservations)) {
      res.reservations = res.reservations.map((r: any) => ({
        ...r,
        status: r.status === 'ACTIVE' ? 'Active' : 'Cancelled',
      }));
    }
    return res;
  },

  cancel: async (reservationId: number): Promise<{ success: boolean; reservation: Reservation }> => {
    const res = await apiRequest(`/reservations/${reservationId}/cancel/`, {
      method: 'POST',
    });
    if (res.reservation && typeof res.reservation.status === 'string') {
      res.reservation.status = res.reservation.status === 'ACTIVE' ? 'Active' : 'Cancelled';
    }
    return res;
  },
};

// Resources API
export const resourcesApi = {
  list: async (type?: string): Promise<{ success: boolean; resources: Resource[] }> => {
    const query = new URLSearchParams();
    if (type) query.set('type', type);

    const res = await apiRequest(`/resources/${query.toString() ? `?${query.toString()}` : ''}`);
    if (res.resources && Array.isArray(res.resources)) {
      res.resources = res.resources.map((r: any) => ({
        ...r,
        // map server enum ROOM/EQUIPMENT -> friendly Room/Equipment
        type: r.type === 'ROOM' ? 'Room' : 'Equipment',
      }));
    }
    return res;
  },

  create: async (data: {
    name: string;
    type: 'Room' | 'Equipment';
    max_bookings: number;
    color_code: string;
  }): Promise<{ success: boolean; resource: Resource }> => {
    // convert friendly type to server enum
    const payload = { ...data, type: data.type === 'Room' ? 'ROOM' : 'EQUIPMENT' };
    const res = await apiRequest('/resources/create/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (res.resource) {
      res.resource.type = res.resource.type === 'ROOM' ? 'Room' : 'Equipment';
    }
    return res;
  },
};

// TimeSlots API
export const timeslotsApi = {
  list: async (params: {
    resource_id?: number;
    date?: string;
  }): Promise<{ success: boolean; timeslots: TimeSlot[] }> => {
    const queryParams = new URLSearchParams();
    if (params.resource_id) queryParams.set('resource_id', params.resource_id.toString());
    if (params.date) queryParams.set('date', params.date);

    const queryString = queryParams.toString();
    return apiRequest(`/timeslots/${queryString ? `?${queryString}` : ''}`);
  },

  generate: async (data: {
    resource_id: number;
    start_date: string;
    end_date: string;
    duration_minutes?: number;
  }): Promise<{ success: boolean; message: string }> => {
    return apiRequest('/timeslots/generate/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
