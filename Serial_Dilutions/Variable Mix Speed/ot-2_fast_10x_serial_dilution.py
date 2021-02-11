import sys
from opentrons import protocol_api

""" 10X Serial Dilution: Instructions for OT-2

Procedure to run up to six instances of 10X serial dilutions per OT-2 unit.
"""

metadata = {
    'protocolName': '10X Serial Dilution',
    'apiLevel': '2.2'
    }

""" Overall Parameters: Sets number of instances and serial dilutions

instances: Number of total instances (an instance involves tipracks, 
           one plate, and the trash bin) as an integer between 1 and 6 
           inclusive
filled_columns: Number of columns in each well to be filled

Note: If-statement check only applies to cases of the 96 well and tiprack.
"""

instances = 0
filled_columns = 6

if instances == 6 and filled_columns > 10:
    print('ERROR: Too many columns need to be filled for the number of '
          'tipracks available. Program exiting.')
    sys.exit()

def how_many(num):
    """ how_many(num): Helper function for switch statement
    
    Converts the instances integer to the
    appropriate switch class (see below) attribute name.
    """

    if num == 6:
        return 'six'
    elif num == 5:
        return 'five'
    elif num == 4:
        return 'four'
    elif num == 3:
        return 'three'
    elif num == 2:
        return 'two'
    elif num == 1:
        return 'one'
    else:
        print('ERROR: Must set instances variable as integer between 1 and 6 '
              'inclusive. Program exiting.')
        return 'default'

def run(protocol: protocol_api.ProtocolContext):

    """ Protocol Parameters Section
    
    Specifies plates, tipracks, pipette, and protocol-specific values. Naming 
    is from the Opentrons Labware Library ( https://labware.opentrons.com/ ).

    tiprack_type: Name of 96 tiprack
    plate_type: Name of 96 plate
    pipette_type: Name of multichannel pipette
    dilution_volume: Volume to transfer by pipette in microliters (uL)
    mix_repetitions: Number of mixes to be done by the pipette
    mix_volume: Volume to mix by pipette in microliters (uL)
    mix_rate: Factor of mix speed (speed of aspiration and dispensation; 
                                   1.0 is the default speed, 
                                   2.0 is twice the default speed, 
                                   0.5 is half the default speed, etc.)
    """

    tiprack_type = 'opentrons_96_filtertiprack_200ul'
    plate_type = 'corning_96_wellplate_360ul_flat'
    pipette_type = 'p300_multi_gen2'
    dilution_volume = 20
    mix_repetitions = 15
    mix_volume = 20
    mix_rate = 1.0

    dilutionplate_10X_6 = None
    dilutionplate_10X_5 = None
    tiprack_10X_5 = None
    dilutionplate_10X_4 = None
    tiprack_10X_4 = None
    dilutionplate_10X_3 = None
    tiprack_10X_3 = None
    dilutionplate_10X_2 = None
    tiprack_10X_2 = None
    dilutionplate_10X_1 = None
    tiprack_10X_1 = None
    dilutionplate_10X = []
    tiprack_10X = []

    """ Labware Section
    
    For plate, use format plate = protocol.load_labware('name', 'slot'), 
    same applies to tiprack. This is for dictating the starting layout.
        
    Optimal slot layout of OT-2 (Slot 12 == XX == trash; P# == plate number;
                                 T# == tiprack number):

     Placements     Slot Numbers
    ************    ************
    * T2 P2 XX *    * 10 11 12 *
    * P3 T1 P1 *    * 7  8  9  *
    * T3 P4 T4 *    * 4  5  6  *
    * P6 T5 P5 *    * 1  2  3  *
    ************    ************

    switch: Switch statement that sets up OT-2 slots depending on specified 
            number of instances
    getattr(object, name[, default]): Executes switch statement
    """

    class switch:
        def six():
            dilutionplate_10X_6 = protocol.load_labware(plate_type, 1)
            dilutionplate_10X.append(dilutionplate_10X_6)
            switch.five()
        def five():
            tiprack_10X_5 = protocol.load_labware(tiprack_type, 2)
            tiprack_10X.append(tiprack_10X_5)
            dilutionplate_10X_5 = protocol.load_labware(plate_type, 3)
            dilutionplate_10X.append(dilutionplate_10X_5)
            switch.four()
        def four():
            tiprack_10X_4 = protocol.load_labware(tiprack_type, 6)
            tiprack_10X.append(tiprack_10X_4)
            dilutionplate_10X_4 = protocol.load_labware(plate_type, 5)
            dilutionplate_10X.append(dilutionplate_10X_4)
            switch.three()
        def three():
            tiprack_10X_3 = protocol.load_labware(tiprack_type, 4)
            tiprack_10X.append(tiprack_10X_3)
            dilutionplate_10X_3 = protocol.load_labware(plate_type, 7)
            dilutionplate_10X.append(dilutionplate_10X_3)
            switch.two()
        def two():
            tiprack_10X_2 = protocol.load_labware(tiprack_type, 10)
            tiprack_10X.append(tiprack_10X_2)
            dilutionplate_10X_2 = protocol.load_labware(plate_type, 11)
            dilutionplate_10X.append(dilutionplate_10X_2)
            switch.one()
        def one():            	
            tiprack_10X_1 = protocol.load_labware(tiprack_type, 8)
            tiprack_10X.append(tiprack_10X_1)
            dilutionplate_10X_1 = protocol.load_labware(plate_type, 9)
            dilutionplate_10X.append(dilutionplate_10X_1)
        def default():
            sys.exit()

    getattr(switch, how_many(instances), 'default')()

    """ Pipettes Section
    
    Pipette will be loaded on the right side of the mount.
    """

    right_pipette = protocol.load_instrument(pipette_type, 'right', 
                                             tip_racks=tiprack_10X)

    """ Commands Section
    
    Loops commands up to six times per OT-2 unit.
    
    Example procedure:
    * Pick up a tip (implicitly from the tiprack you specified and assigned to 
      the pipette): pipette.pick_up_tip()
    * Aspirate 100 µL from well row A1 of the 96 well plate you specified:
      pipette.aspirate(100, plate['A1'])
    * Dispense 100 µL into well row A2 of the 96 well plate you specified:
      pipette.dispense(100, plate['A2'])
    * Drop the tip (implicitly into the trash at the back right of the robot’s 
      deck): pipette.drop_tip()

    Note: plate['A1'] == plate.columns()[0][0]
          plate['A2'] == plate.columns()[1][0]
    """

    for i in range(instances):
        right_pipette.pick_up_tip()
        right_pipette.mix(mix_repetitions, mix_volume, 
                          dilutionplate_10X[i].columns()[0][0])
        right_pipette.drop_tip()

        for j in range(filled_columns - 1): # indices start at zero
            right_pipette.pick_up_tip()
            right_pipette.aspirate(dilution_volume, 
                                   dilutionplate_10X[i].columns()[j][0])
            right_pipette.dispense(dilution_volume, 
                                   dilutionplate_10X[i].columns()[j+1][0])
            right_pipette.mix(mix_repetitions, mix_volume, rate=mix_rate)
            right_pipette.drop_tip()