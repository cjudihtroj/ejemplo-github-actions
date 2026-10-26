@HU-01 @web
Feature: Inicio de sesión del administrador
  Como administrador del hotel
  quiero iniciar sesión en el panel
  para gestionar habitaciones, reservas y mensajes

  @CP-01
  Scenario: Iniciar sesión con rol administrador y crear una habitación
    Given que el administrador está en la página de login
    When inicia sesión con usuario "admin" y clave "password"
    Then ve el panel de administración
    And valida que se muestre la sección de habitaciones
    When crea una habitación "Double" accesible con precio 150
    Then la nueva habitación aparece en el listado con tipo "Double" y precio 150

  @CP-02
  Scenario: Iniciar sesión con clave incorrecta
    Given que el administrador está en la página de login
    When inicia sesión con usuario "admin" y clave "incorrecta"
    Then ve el mensaje "Invalid credentials"

  @CP-11
  Scenario: Iniciar sesión y eliminar una habitación
    Given que el administrador inició sesión
    And creó una habitación "Single" accesible con precio 100
    When elimina la habitación
    Then la habitación ya no aparece en el listado
