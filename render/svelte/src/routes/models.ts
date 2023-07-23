

export interface RailwayInformation {
    northbound: DeparturesResponse;
    southbound: DeparturesResponse;
}

export interface LocationDetails {
    locationName: string;
    crs: string;
    via?: string | null;
    futureChangeTo?: string | null;
    assocIsCancelled?: boolean | null;
}

export interface Location {
    location: LocationDetails[];
}

export interface Formation {
    avgLoading: number;
    coaches?: string | null;
}

export interface Service {
    sta?: string | null;
    eta?: string | null;
    std: string;
    etd: string;
    platform?: string | null;
    operator: string;
    operatorCode: string;
    isCircularRoute?: boolean | null;
    isCancelled?: boolean | null;
    filterLocationCancelled?: boolean | null;
    serviceType: string;
    length?: string | null;
    detachFront?: boolean | null;
    isReverseFormation?: boolean | null;
    cancelReason?: string | null;
    delayReason?: string | null;
    serviceID: string;
    adhocAlerts?: string | null;
    rsid?: string | null;
    origin: Location;
    destination: Location;
    currentOrigins?: Location | null;
    currentDestinations?: Location | null;
    formation?: Formation | null;
}

export interface TrainServices {
    service: Service[];
}

export interface Message {
    _value_1: string;
}

export interface NrccMessages {
    message: Message[];
}

export interface DeparturesResponse {
    generatedAt: string;
    locationName: string;
    crs: string;
    filterLocationName: string;
    filtercrs: string;
    filterType: string | null;
    nrccMessages: NrccMessages | null;
    platformAvailable: boolean;
    areServicesAvailable: boolean | null;
    trainServices?: TrainServices | null;
    busServices?: string | null;
    ferryServices?: string | null;
}

export interface Weather {
    id: number;
    main: string;
    description: string;
    icon: string;
}

export interface Main {
    temp: number;
    feels_like: number;
    temp_min: number;
    temp_max: number;
    pressure: number;
    humidity: number;
}

export interface Wind {
    speed: number;
    deg: number;
}

export interface Clouds {
    all: number;
}

export interface Sys {
    type: number;
    id: number;
    country: string;
    sunrise: string;
    sunset: string;
}
export interface Coordinates {
    lon: number;
    lat: number;
}

export interface WeatherData {
    coord: Coordinates;
    weather: Weather[];
    base: string;
    main: Main;
    visibility: number;
    wind: Wind;
    clouds: Clouds;
    dt: string;
    sys: Sys;
    timezone: number;
    id: number;
    name: string;
    cod: number;
}

export interface AirQualityData {
    coord: {
        lon: number;
        lat: number;
    };
    list: AirQualityItem[];
}

export interface AirQualityItem {
    dt: string;
    main: {
        aqi: number;
    };
    components: {
        co: number;
        no: number;
        no2: number;
        o3: number;
        so2: number;
        pm2_5: number;
        pm10: number;
        nh3: number;
    };
}

interface Temperature {
    indoor: number;
    outdoor: number;
}

export interface AirconData {
    name: string;
    temperature: Temperature;
    humidity: number;
}


export interface DashboardInputData {
    rail: RailwayInformation;
    weather: WeatherData;
    time: string;
    air_quality: AirQualityData
    aircon: AirconData[]
}

export interface Train {
    time: string;
    destination: string;
    status: string;
    delay: string;
}