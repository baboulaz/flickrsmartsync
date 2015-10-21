import logging
import re
from subprocess import Popen, PIPE

logger = logging.getLogger("flickrsmartsync")


class Hash(object):
    md5_machine_tag_prefix = "checksum:md5="
    sha1_machine_tag_prefix = "checksum:sha1="
    checksum_pattern = "[0-9a-f]{32,40}"
    
    def __init__(self, cmd_args):
        self.cmd_args = cmd_args

    def checksum(self,filename,typeCheck):
        result = Popen([typeCheck+"sum",filename],stdout=PIPE).communicate()[0]
        m = re.search('^('+self.checksum_pattern+')',result.strip())
        if not m:
            raise Exception, "Output from "+typeCheck+"sum was unexpected: "+result
        return m.group(1)

    def md5sum(self,filename):
        return self.checksum(filename,"md5")

    def sha1sum(self,filename):
        return self.checksum(filename,"sha1")

    def get_flickr_photo_checksums(self,photo):
        info_result = self.flickr.photos_getInfo(photo_id=photo.attrib['id'])
        result = {} 
        for t in info_result.getchildren()[0].find('tags'):
            m_md5 = re.search('^'+self.md5_machine_tag_prefix+'('+self.checksum_pattern+')$',t.attrib['raw'])
            if m_md5 and len(m_md5.group(1)) == 32:
                print "Got MD5sum machine tag"
                result['md5'] = m_md5.group(1)
            m_sha1 = re.search('^'+self.sha1_machine_tag_prefix+'('+self.checksum_pattern+')$',t.attrib['raw'])
            if m_sha1 and len(m_sha1.group(1)) == 40:
                print "Got SHA1sum machine tag"
                result['sha1'] = m_sha1.group(1)
            elif m_sha1 and len(m_sha1.group(1)) == 32:
                print "Found a truncated SHA1sum tag, so removing it:"
                self.flickr.photos_removeTag(tag_id=t.attrib['id'])
        return result