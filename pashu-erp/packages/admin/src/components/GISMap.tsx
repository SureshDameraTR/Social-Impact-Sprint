"use client";

import dynamic from "next/dynamic";
import { Box, CircularProgress } from "@mui/material";

const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
);
const CircleMarker = dynamic(
  () => import("react-leaflet").then((mod) => mod.CircleMarker),
  { ssr: false }
);
const Popup = dynamic(
  () => import("react-leaflet").then((mod) => mod.Popup),
  { ssr: false }
);
const LayersControl = dynamic(
  () => import("react-leaflet").then((mod) => mod.LayersControl),
  { ssr: false }
);
const LayerGroup = dynamic(
  () => import("react-leaflet").then((mod) => mod.LayerGroup),
  { ssr: false }
);
const Marker = dynamic(
  () => import("react-leaflet").then((mod) => mod.Marker),
  { ssr: false }
);

export interface MapPoint {
  id: string;
  lat: number;
  lng: number;
  label: string;
  details?: string;
  severity?: "critical" | "high" | "medium" | "low";
  type?: "alert" | "center" | "farmer";
}

const severityColor: Record<string, string> = {
  critical: "#d32f2f",
  high: "#f57c00",
  medium: "#fbc02d",
  low: "#388e3c",
};

interface GISMapProps {
  center?: [number, number];
  zoom?: number;
  points?: MapPoint[];
  height?: string | number;
  showLayers?: boolean;
}

export default function GISMap({
  center = [12.3, 76.6],
  zoom = 8,
  points = [],
  height = 400,
  showLayers = false,
}: GISMapProps) {
  const alerts = points.filter((p) => p.type === "alert" || p.severity);
  const centers = points.filter((p) => p.type === "center");
  const farmers = points.filter((p) => p.type === "farmer");

  return (
    <Box
      sx={{
        height,
        width: "100%",
        borderRadius: 2,
        overflow: "hidden",
        "& .leaflet-container": { height: "100%", width: "100%" },
      }}
    >
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {showLayers ? (
          <LayersControl position="topright">
            <LayersControl.Overlay checked name="Disease Alerts">
              <LayerGroup>
                {alerts.map((pt) => (
                  <CircleMarker
                    key={pt.id}
                    center={[pt.lat, pt.lng]}
                    radius={10}
                    pathOptions={{
                      color: severityColor[pt.severity || "medium"],
                      fillColor: severityColor[pt.severity || "medium"],
                      fillOpacity: 0.6,
                    }}
                  >
                    <Popup>
                      <strong>{pt.label}</strong>
                      {pt.details && <br />}
                      {pt.details}
                    </Popup>
                  </CircleMarker>
                ))}
              </LayerGroup>
            </LayersControl.Overlay>
            <LayersControl.Overlay checked name="Milk Centers">
              <LayerGroup>
                {centers.map((pt) => (
                  <CircleMarker
                    key={pt.id}
                    center={[pt.lat, pt.lng]}
                    radius={8}
                    pathOptions={{
                      color: "#0288d1",
                      fillColor: "#0288d1",
                      fillOpacity: 0.6,
                    }}
                  >
                    <Popup>
                      <strong>{pt.label}</strong>
                      {pt.details && <br />}
                      {pt.details}
                    </Popup>
                  </CircleMarker>
                ))}
              </LayerGroup>
            </LayersControl.Overlay>
            <LayersControl.Overlay name="Farmer Locations">
              <LayerGroup>
                {farmers.map((pt) => (
                  <CircleMarker
                    key={pt.id}
                    center={[pt.lat, pt.lng]}
                    radius={5}
                    pathOptions={{
                      color: "#388e3c",
                      fillColor: "#388e3c",
                      fillOpacity: 0.5,
                    }}
                  >
                    <Popup>
                      <strong>{pt.label}</strong>
                      {pt.details && <br />}
                      {pt.details}
                    </Popup>
                  </CircleMarker>
                ))}
              </LayerGroup>
            </LayersControl.Overlay>
          </LayersControl>
        ) : (
          alerts.map((pt) => (
            <CircleMarker
              key={pt.id}
              center={[pt.lat, pt.lng]}
              radius={10}
              pathOptions={{
                color: severityColor[pt.severity || "medium"],
                fillColor: severityColor[pt.severity || "medium"],
                fillOpacity: 0.6,
              }}
            >
              <Popup>
                <strong>{pt.label}</strong>
                {pt.details && <br />}
                {pt.details}
              </Popup>
            </CircleMarker>
          ))
        )}
      </MapContainer>
    </Box>
  );
}
