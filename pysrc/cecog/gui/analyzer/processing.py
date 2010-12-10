"""
                           The CellCognition Project
                     Copyright (c) 2006 - 2010 Michael Held
                      Gerlich Lab, ETH Zurich, Switzerland
                              www.cellcognition.org

              CellCognition is distributed under the LGPL License.
                        See trunk/LICENSE.txt for details.
                 See trunk/AUTHORS.txt for author contributions.
"""

__author__ = 'Michael Held'
__date__ = '$Date$'
__revision__ = '$Rev$'
__source__ = '$URL$'

__all__ = ['ProcessingFrame']

#-------------------------------------------------------------------------------
# standard library imports:
#

#-------------------------------------------------------------------------------
# extension module imports:
#

#-------------------------------------------------------------------------------
# cecog imports:
#
from cecog.traits.analyzer.processing import SECTION_NAME_PROCESSING
from cecog.gui.analyzer import (_BaseFrame,
                                _ProcessorMixin,
                                AnalzyerThread,
                                HmmThread,
                                )
from cecog.analyzer import (SECONDARY_REGIONS,
                            TERTIARY_REGIONS,
                            SECONDARY_COLORS,
                            )
from cecog.analyzer.channel import (PrimaryChannel,
                                    SecondaryChannel,
                                    TertiaryChannel,
                                    )

#-------------------------------------------------------------------------------
# constants:
#


#-------------------------------------------------------------------------------
# functions:
#


#-------------------------------------------------------------------------------
# classes:
#
class ProcessingFrame(_BaseFrame, _ProcessorMixin):

    SECTION_NAME = SECTION_NAME_PROCESSING

    def __init__(self, settings, parent):
        _BaseFrame.__init__(self, settings, parent)
        _ProcessorMixin.__init__(self)

        self.register_control_button('process',
                                     [AnalzyerThread,
                                      HmmThread],
                                     ('Start processing', 'Stop processing'))

        self.add_group(None,
                       [('primary_featureextraction', (0,0,1,1)),
                        ('primary_classification', (1,0,1,1)),
                        ('tracking', (2,0,1,1)),
                        ('tracking_synchronize_trajectories', (3,0,1,1)),
                        ('primary_errorcorrection', (4,0,1,1))
                        ], link='primary_channel', label='Primary channel')

        for prefix in ['secondary', 'tertiary']:
            self.add_group('%s_processchannel' % prefix,
                           [('%s_featureextraction' % prefix, (0,0,1,1)),
                            ('%s_classification' % prefix, (1,0,1,1)),
                            ('%s_errorcorrection' % prefix, (2,0,1,1))
                            ])

        #self.add_line()

        self.add_expanding_spacer()

        self._init_control()

    @classmethod
    def get_special_settings(cls, settings):
        settings = _ProcessorMixin.get_special_settings(settings)

        settings.set('General', 'rendering', {})
        settings.set('General', 'rendering_class', {})

        additional_prefixes = [SecondaryChannel.PREFIX, TertiaryChannel.PREFIX]

        settings.set_section('Classification')
        sec_class_regions = dict([(prefix,
                                  settings.get2('%s_classification_regionname' % prefix))
                                  for prefix in additional_prefixes])

        settings.set_section('ObjectDetection')
        prim_id = PrimaryChannel.NAME
        sec_ids = dict([(x.PREFIX, x.NAME)
                        for x in [SecondaryChannel, TertiaryChannel]])
        sec_regions = dict([(prefix, [v for k,v in regions.iteritems()
                                      if settings.get2(k)])
                            for prefix, regions in
                            [(SecondaryChannel.PREFIX, SECONDARY_REGIONS),
                             (TertiaryChannel.PREFIX, TERTIARY_REGIONS),
                             ]])

#        lookup = dict([(v,k) for k,v in SECONDARY_REGIONS.iteritems()])
#        # FIXME: we should rather show a warning here!
#        if not sec_region in sec_regions:
#            sec_regions.append(sec_region)
#            settings.set2(lookup[sec_region], True)

        show_ids = settings.get('Output', 'rendering_contours_showids')
        show_ids_class = settings.get('Output', 'rendering_class_showids')

        settings.get('General', 'rendering').update({'primary_contours': {prim_id: {'raw': ('#FFFFFF', 1.0),
                                                                                    'contours': {'primary': ('#FF0000', 1, show_ids)}}}})

        settings.set_section('Processing')
        if settings.get2('primary_classification'):
            settings.get('General', 'rendering_class').update({'primary_classification': {prim_id: {'raw': ('#FFFFFF', 1.0),
                                                                                          'contours': [('primary', 'class_label', 1, False),
                                                                                                       ('primary', '#000000', 1, show_ids_class),
                                                                                                       ]}}})

        for prefix in additional_prefixes:
            if settings.get2('%s_processchannel' % prefix):
                sec_id = sec_ids[prefix]
                settings.get('General', 'rendering').update(dict([('%s_contours_%s' % (prefix, x), {sec_id: {'raw': ('#FFFFFF', 1.0),
                                                                                                             'contours': [(x, SECONDARY_COLORS[x] , 1, show_ids)]
                                                                                                 }})
                                                                  for x in sec_regions[prefix]]))

                if settings.get2('%s_classification' % prefix):
                    sec_id = sec_ids[prefix]
                    sec_region = sec_class_regions[prefix]
                    settings.get('General', 'rendering_class').update({'%s_classification_%s' % (prefix, sec_region): {sec_id: {'raw': ('#FFFFFF', 1.0),
                                                                                                                             'contours': [(sec_region, 'class_label', 1, False),
                                                                                                                                          (sec_region, '#000000', 1, show_ids_class),
                                                                                                                                          ]}}})
            else:
                settings.set2('%s_classification' % prefix, False)
                settings.set2('%s_errorcorrection' % prefix, False)

        return settings