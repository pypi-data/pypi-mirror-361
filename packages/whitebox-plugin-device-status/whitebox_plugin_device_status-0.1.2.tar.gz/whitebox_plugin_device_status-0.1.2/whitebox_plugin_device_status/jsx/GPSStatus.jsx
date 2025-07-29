import { useEffect } from "react";
import useDevicesStore from "./stores/devices";
const { importWhiteboxComponent } = Whitebox;

const DeviceConnection = importWhiteboxComponent(
  "device-wizard.device-connection"
);

const GPSStatus = () => {
  const gpsConnected = useDevicesStore((state) => state.gpsConnected);
  const gpsSolution = useDevicesStore((state) => state.gpsSolution);
  const gpsAccuracy = useDevicesStore((state) => state.gpsAccuracy);
  const updateGPSStatus = useDevicesStore((state) => state.updateGPSStatus);

  useEffect(() => {
    return Whitebox.sockets.addEventListener("flight", "message", (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "status_update") {
        updateGPSStatus({ data });
      }
    });
  });

  const getDeviceName = () => {
    if (!gpsConnected) return "GPS - " + gpsSolution;
    return `GPS - ${gpsSolution}, ${gpsAccuracy.toFixed(2)}m`;
  };

  return (
    <DeviceConnection deviceName={getDeviceName()} isConnected={gpsConnected} />
  );
};

export { GPSStatus };
export default GPSStatus;
