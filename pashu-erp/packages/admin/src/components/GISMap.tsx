"use client";

import { useEffect } from "react";
import dynamic from "next/dynamic";
import { Box } from "@mui/material";

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

/* Inner component that uses react-leaflet directly (no dynamic per-component) */
function MapInner({
  center,
  zoom,
  points,
  showLayers,
}: {
  center: [number, number];
  zoom: number;
  points: MapPoint[];
  showLayers: boolean;
}) {
  useEffect(() => {
    const id = 'leaflet-css';
    if (!document.getElementById(id)) {
      const link = document.createElement('link');
      link.id = id;
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }
  }, []);
  /* eslint-disable @typescript-eslint/no-var-requires */
  const RL = require("react-leaflet") as typeof import("react-leaflet");
  const {
    MapContainer,
    TileLayer,
    CircleMarker,
    Popup,
    LayersControl,
    LayerGroup,
  } = RL;

  const alerts = points.filter((p) => p.type === "alert" || p.severity);
  const centers = points.filter((p) => p.type === "center");
  const farmers = points.filter((p) => p.type === "farmer");

  return (
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
              {alerts.map((pt: MapPoint) => (
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
              {centers.map((pt: MapPoint) => (
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
              {farmers.map((pt: MapPoint) => (
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
        alerts.map((pt: MapPoint) => (
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
  );
}

/* Dynamic wrapper -- SSR disabled for the entire map */
const DynamicMap = dynamic(() => Promise.resolve(MapInner), {
  ssr: false,
  loading: () => (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#f0f4f3",
        borderRadius: 2,
        color: "#5f7a74",
        fontSize: 14,
      }}
    >
      Loading map...
    </Box>
  ),
});

export default function GISMap({
  center = [12.3, 76.6],
  zoom = 8,
  points = [],
  height = 400,
  showLayers = false,
}: GISMapProps) {
  return (
    <Box
      aria-label="Map"
      sx={{
        height,
        width: "100%",
        borderRadius: 2,
        overflow: "hidden",
        "& .leaflet-container": { height: "100%", width: "100%" },
      }}
    >
      <DynamicMap
        center={center}
        zoom={zoom}
        points={points}
        showLayers={showLayers}
      />
    </Box>
  );
}
