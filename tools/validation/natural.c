/* Natural joypad-only fixture route. No CPU/register/memory injection. */
#include <mgba/flags.h>
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/directories.h>
#include <mgba/internal/gb/gb.h>
#include <mgba/internal/sm83/sm83.h>
#include <mgba-util/vfs.h>
#include <mgba-util/image.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void snapshot(struct mCore*c,const char*dir,int stage) {
 unsigned w,h;c->currentVideoSize(c,&w,&h);const void*p;size_t stride;c->getPixels(c,&p,&stride);
 char path[512];snprintf(path,sizeof(path),"%s/stage-%02d.ppm",dir,stage);FILE*f=fopen(path,"wb");
 if(!f)return;fprintf(f,"P6\n%u %u\n255\n",w,h);const mColor*pix=p;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){mColor v=pix[y*stride+x];fputc(M_R8(v),f);fputc(M_G8(v),f);fputc(M_B8(v),f);}fclose(f);
 struct GB*g=c->board;printf("stage=%d frame=%u pc=%04X A=%u B=%u fixtureFrames=%u held=%02X pressed=%02X counters=",stage,c->frameCounter(c),g->cpu->pc,g->memory.currentBank,g->memory.currentBank1,c->busRead8(c,0xD800),c->busRead8(c,0xD802),c->busRead8(c,0xD801));for(int i=0;i<8;i++)printf("%02X",c->busRead8(c,0xD803+i));printf(" exitCode=%02X IE=%02X IF=%02X IME=%d FF8A=%02X joy=%02X STAT=%02X LCDC=%02X LY=%02X SP=%04X halted=%d pending=%d FF8E=%02X FF8F=%02X\n",c->busRead8(c,0xC671),c->busRead8(c,0xFFFF),c->busRead8(c,0xFF0F),g->memory.ime,c->busRead8(c,0xFF8A),c->busRead8(c,0xFF96),c->busRead8(c,0xFF41),c->busRead8(c,0xFF40),c->busRead8(c,0xFF44),g->cpu->sp,g->cpu->halted,g->cpu->irqPending,c->busRead8(c,0xFF8E),c->busRead8(c,0xFF8F));
}
int main(int argc,char**argv){if(argc<4)return 2;struct mCore*c=mCoreFind(argv[1]);if(!c||!c->init(c))return 3;mCoreInitConfig(c,"natural-pad-test");if(!mCoreLoadFile(c,argv[1]))return 4;c->dirs.save=VDirOpen(argv[2]);strcpy(c->dirs.baseName,"padtest");if(!mCoreAutoloadSave(c))return 5;mColor*video=calloc(256*256,sizeof(mColor));c->setVideoBuffer(c,video,256);c->reset(c);
 for(int i=3;i<argc;i++){unsigned key,frames;if(sscanf(argv[i],"%u:%u",&key,&frames)!=2)return 6;c->setKeys(c,key);for(unsigned j=0;j<frames;j++)c->runFrame(c);snapshot(c,argv[2],i-3);}
 c->setKeys(c,0);c->unloadROM(c);mCoreConfigDeinit(&c->config);c->deinit(c);free(video);return 0;}
