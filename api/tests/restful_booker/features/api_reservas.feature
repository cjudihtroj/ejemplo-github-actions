@HU-02 @api
Feature: API de reservas de Restful Booker
  Como integrador del sistema del hotel
  quiero consultar, crear y eliminar reservas por la API
  para conectar otros sistemas con las reservas

  @CP-03
  Scenario: Consultar una reserva existente
    Given que existe una reserva a nombre de "Utec" con precio total 120
    When se consulta la reserva por su identificador
    Then la respuesta tiene el estado 200
    And la respuesta tiene el apellido "Utec" y el precio total 120

  @CP-04
  Scenario: Consultar una reserva que no existe
    When se consulta la reserva con identificador 999999999
    Then la respuesta tiene el estado 404

  @CP-05
  Scenario: Crear una reserva con datos válidos
    When se crea una reserva a nombre de "Utec" con precio total 150
    Then la respuesta tiene el estado 200
    And la respuesta incluye el identificador de la nueva reserva

  @CP-06
  Scenario: Eliminar una reserva sin autenticación
    Given que existe una reserva a nombre de "Utec" con precio total 120
    When se elimina la reserva sin token
    Then la respuesta tiene el estado 403
