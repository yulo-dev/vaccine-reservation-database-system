CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Availabilities (
    Date date,
    Caregiver_Username varchar(255) REFERENCES Caregivers(Username),
    PRIMARY KEY (Date, Caregiver_Username)
);

CREATE TABLE Appointments (
    ID int,
    Date date,
    Vaccine_Name varchar(255) REFERENCES Vaccines(Name),
    Patient_Username varchar(255) REFERENCES Patients(Username),
    Caregiver_Username varchar(255) REFERENCES Caregivers(Username),
    PRIMARY KEY (ID)
);