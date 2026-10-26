@HU-01 @web
Feature: Inicio de sesión del administrador
  Como administrador del hotel
  quiero iniciar sesión en el panel
  para gestionar habitaciones, reservas y mensajes

  @CP-01
  Scenario: Iniciar sesión con credenciales correctas
    Given que el administrador está en la página de login
    When inicia sesión con usuario "admin" y clave "password"
    Then ve el panel de administración
    And valida que se muestre la sección de habitaciones

  @CP-02
  Scenario: Iniciar sesión con clave incorrecta
    Given que el administrador está en la página de login
    When inicia sesión con usuario "admin" y clave "incorrecta"
    Then ve el mensaje "Invalid credentials"
