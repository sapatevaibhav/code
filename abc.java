// abc.java
// Demonstrating inheritance and abstraction in Java

// Abstract class
abstract class Vehicle {
    // Properties
    protected String brand;
    protected String model;
    protected int year;

    // Constructor
    public Vehicle(String brand, String model, int year) {
        this.brand = brand;
        this.model = model;
        this.year = year;
    }

    // Abstract method (to be implemented by subclasses)
    public abstract void startEngine();

    // Concrete method
    public void displayInfo() {
        System.out.println("Vehicle: " + brand + " " + model + " (" + year + ")");
    }

    // Another abstract method
    public abstract double calculateFuelEfficiency();
}

// Subclass implementing abstract class
class Car extends Vehicle {
    private int numberOfDoors;
    private double engineSize;

    public Car(String brand, String model, int year, int numberOfDoors, double engineSize) {
        super(brand, model, year);
        this.numberOfDoors = numberOfDoors;
        this.engineSize = engineSize;
    }

    @Override
    public void startEngine() {
        System.out.println("Car engine started with key ignition");
    }

    @Override
    public double calculateFuelEfficiency() {
        return 100.0 / (engineSize * 5); // Simple calculation for demonstration
    }

    public void honk() {
        System.out.println("Beep beep!");
    }
}

// Another subclass implementing abstract class
class Motorcycle extends Vehicle {
    private boolean hasSidecar;

    public Motorcycle(String brand, String model, int year, boolean hasSidecar) {
        super(brand, model, year);
        this.hasSidecar = hasSidecar;
    }

    @Override
    public void startEngine() {
        System.out.println("Motorcycle engine started with kick start");
    }

    @Override
    public double calculateFuelEfficiency() {
        return hasSidecar ? 40.5 : 55.2; // Different efficiency based on sidecar presence
    }

    public void doWheelie() {
        if (!hasSidecar) {
            System.out.println("Performing a wheelie!");
        } else {
            System.out.println("Cannot do wheelie with sidecar attached!");
        }
    }
}

// Main class to demonstrate inheritance and abstraction
public class abc {
    public static void main(String[] args) {
        // Cannot instantiate abstract class
        // Vehicle vehicle = new Vehicle("Generic", "Model", 2023); // This would cause error

        Car car = new Car("Toyota", "Corolla", 2023, 4, 1.8);
        Motorcycle motorcycle = new Motorcycle("Honda", "CBR", 2023, false);

        // Polymorphism - treating car and motorcycle as their parent type
        Vehicle vehicle1 = car;
        Vehicle vehicle2 = motorcycle;

        // Calling methods
        System.out.println("--- Car Information ---");
        car.displayInfo();
        car.startEngine();
        System.out.println("Fuel efficiency: " + car.calculateFuelEfficiency() + " km/l");
        car.honk();

        System.out.println("\n--- Motorcycle Information ---");
        motorcycle.displayInfo();
        motorcycle.startEngine();
        System.out.println("Fuel efficiency: " + motorcycle.calculateFuelEfficiency() + " km/l");
        motorcycle.doWheelie();

        System.out.println("\n--- Using Polymorphism ---");
        vehicle1.displayInfo();
        vehicle1.startEngine();
        vehicle2.displayInfo();
        vehicle2.startEngine();
    }
}
