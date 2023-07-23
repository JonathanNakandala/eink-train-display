export const prerender = true;

import { onMount } from "svelte";
import type {
    DashboardInputData,
    RailwayInformation,
    DeparturesResponse,
    LocationDetails,
    Location,
    Formation,
    Service,
    TrainServices,
    Message,
    NrccMessages,
    Weather,
    Main,
    Wind,
    Clouds,
    Sys,
    Coordinates,
    WeatherData,
} from './models';


interface Train {
    time: string;
    destination: string;
    status: string;
    delay: string;
}
let currentTime: string, currentDay: string, currentDate: string;
let northboundTrains: Train[] = [], southboundTrains: Train[] = [];
let currentTemperature: string, minTemperature: string, maxTemperature: string;




const loadData = (data: DashboardInputData) => {
    const parsedTime = new Date(data.time);

    currentTime = parsedTime.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    currentDay = parsedTime.toLocaleDateString('en-GB', { weekday: 'short' }).toUpperCase();
    currentDate = parsedTime.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }).toUpperCase();

    northboundTrains = data.rail.northbound.trainServices?.service.map((service: Service) => ({
        time: service.std,
        destination: service.destination.location[0].locationName,
        status: service.etd,
        delay: getDelay(service, parsedTime)
    })) || [];

    southboundTrains = data.rail.southbound.trainServices?.service.map((service: Service) => ({
        time: service.std,
        destination: service.destination.location[0].locationName,
        status: service.etd,
        delay: getDelay(service, parsedTime)
    })) || [];

    currentTemperature = `${data.weather.main.temp}°C`;
    minTemperature = `${data.weather.main.temp_min}°C`;
    maxTemperature = `${data.weather.main.temp_max}°C`;
};

const loadDataFromSource = (path: string) => {
    fetch(path)
        .then(response => response.json() as Promise<DashboardInputData>)
        .then(data => {
            loadData(data);
        })
        .catch((error) => console.error('Error:', error));
};







function getDelay(service: Service, now: Date): string {
    const arrivalTime = new Date(now.toISOString().split('T')[0] + 'T' + service.std + ':00');

    // If the arrival time is earlier than now, add one day
    if (arrivalTime < now) {
        arrivalTime.setDate(arrivalTime.getDate() + 1);
    }

    const delayInMinutes = Math.floor((arrivalTime.getTime() - now.getTime()) / 60000); // convert ms to mins
    const delayHours = Math.floor(delayInMinutes / 60);
    const delayMinutes = delayInMinutes % 60;

    if (delayInMinutes > 60) {
        return `${delayHours} HR ${delayMinutes} MINS`;
    } else {
        return `${delayInMinutes} MINS`;
    }
}

