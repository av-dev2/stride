// Shared marker styling so the map and the sidebar never disagree.
export const GPS_COLORS = {
	moving: "#16a34a",
	idle: "#2563eb",
	alarm: "#dc2626",
};

export const MOVING_SPEED_KMH = 2;

export function getMarkerColor(loc) {
	if (loc.alarm_code) return GPS_COLORS.alarm;
	if (parseFloat(loc.speed || 0) > MOVING_SPEED_KMH) return GPS_COLORS.moving;
	return GPS_COLORS.idle;
}

export function getStatusLabel(loc) {
	if (loc.alarm_code) return "Alarm";
	if (parseFloat(loc.speed || 0) > MOVING_SPEED_KMH) return "Moving";
	return "Idle";
}
